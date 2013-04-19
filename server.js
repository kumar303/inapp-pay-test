var express = require('express');
var jwt = require('jwt-simple');
var qs = require('qs');
var pay = require('mozpay');
var uuid = require('node-uuid');

try {
  var localConfig = require('./config');
} catch (er) {
  if (er.code == 'MODULE_NOT_FOUND') {
    console.log('You must create a local config file:');
    console.log('cp config-dist.js config.js');
    console.log('Error:', er);
    return;
  } else {
    throw er;
  }
}

var app = express();
var db = {};  // in-memory database!
var media = __dirname + '/www';


var config = {
  host: '0.0.0.0',
  port: 3000,
  mozPayKey: null,
  mozPaySecret: null,
  mozPayAudience: 'marketplace.firefox.com',
  mozPayType: 'mozilla/payments/pay/v1',
  mozPayRoutePrefix: '/mozpay',
  // When not null, simulate this result instead of making a real purchase.
  simulate: null
};

config.extHost = config.host;
config.extPort = config.port;

localConfig(config);

config.manifestURL = absURL('/manifest.webapp');


function addPort() {
  if (config.extPort) {
    return ':' + config.extPort;
  } else {
    return ''
  }
}

function absURL(path) {
  return 'http://' + config.extHost + addPort() + path;
}

function postbackURL(path) {
   return absURL(config.mozPayRoutePrefix + '/' + path);
}

app.configure(function() {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.set('view options', { layout: false });
  app.use(express.logger({format: 'dev'}));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
});

pay.routes(app, config);

app.get('/', function(req, res) {
  res.render('index', {
    config: config
  });
});

app.get('/jwt-source', function(req, res) {
  var defaultJWT = {
    iss: config.mozPayKey,
    aud: config.mozPayAudience,
    typ: config.mozPayType,
    iat: pay.now(),
    exp: pay.now() + 3600,  // in 1hr
    request: {
      pricePoint: 1,
      id: uuid.v4(),
      name: 'Virtual Kiwi',
      description: 'The forbidden fruit',
      icons: {
        '32': absURL('/img/kiwi_32.png'),
        '48': absURL('/img/kiwi_48.png'),
        '64': absURL('/img/kiwi_64.png'),
        '128': absURL('/img/kiwi_128.png'),
      },
      'productData': '<this is not editable>',
      'chargebackURL': '<this is not editable>',
      'postbackURL': '<this is not editable>'
    }
  };
  if (config.simulate) {
    defaultJWT.request.simulate = config.simulate;
  }
  res.send(JSON.stringify(defaultJWT, null, 2));
});

app.get('/transaction/:trans', function (req, res) {
  var transID = req.params.trans;
  if (!db[transID]) {
    res.send(404);
    return;
  }
  res.send({state: db[transID].state, result: db[transID].result});
});

app.post('/pay', function (req, res) {
  var transID = uuid.v4();
  db[transID] = {state: 'pending', result: null};
  var jwtReq = JSON.parse(req.param('jwt'));
  // fill in non-editable fields.
  jwtReq.request.productData = qs.stringify({localTransID: transID}),
  jwtReq.request.postbackURL = postbackURL('postback');
  jwtReq.request.chargebackURL = postbackURL('chargeback');

  res.send({transID: transID,
            jwt: jwt.encode(jwtReq, config.mozPaySecret, 'HS256')});
});

function processData(data, done) {
  var transID = qs.parse(data.request.productData).localTransID;
  if (!db[transID]) {
    throw new Error('There is no record of transaction ' + transID);
  }
  if (db[transID].state == 'completed') {
    console.log('Transaction', transID, 'ignored.',
                'Attacker may be trying to replay a JWT notice');
    done('already-processed');
    return;
  }
  console.log('transaction completed:', transID);
  db[transID].state = 'completed';
  done(null, db[transID]);
}

pay.on('postback', function(data) {
  console.log('postback received for ' + data.response.transactionID);
  processData(data, function(error, trans) {
    if (!error) {
      trans.result = 'postback';
    }
  });
});

pay.on('chargeback', function(data) {
  console.log('chargeback received for ' + data.response.transactionID);
  processData(data, function(error, trans) {
    if (!error) {
      trans.result = 'chargeback';
    }
  });
});

app.configure(function() {
  app.use(express.static(media));
});


app.listen(config.port, config.host);
console.log('Listening at ' + config.host + ':' + config.port);

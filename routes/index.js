var jwt = require('jwt-simple');
var pay = require('mozpay');
var qs = require('qs');
var uuid = require('node-uuid');

module.exports = function(app, config) {

  app.get('/', function(req, res) {
    res.render('index', {
      config: config
    });
  });

  app.get('/jwt-source', function(req, res) {
    var server = config.servers[req.param('server')];
    if (!server) {
      console.log('/jwt-source: server does not exist for', req.param('server'));
      res.send(400);
      return;
    }
    // WARNING! This will not work with concurrent users on the site.
    // mozpay needs a fix.
    pay.configure(server);

    var defaultJWT = {
      iss: server.mozPayKey,
      aud: server.mozPayAudience,
      typ: server.mozPayType,
      iat: pay.now(),
      exp: pay.now() + 3600,  // in 1hr
      request: {
        pricePoint: 10,
        id: uuid.v4(),
        name: 'Virtual Kiwi',
        description: 'The forbidden fruit',
        icons: {
          '32': config.absURL('/img/kiwi_32.png'),
          '48': config.absURL('/img/kiwi_48.png'),
          '64': config.absURL('/img/kiwi_64.png'),
          '128': config.absURL('/img/kiwi_128.png'),
        },
        'productData': '<this is not editable>',
        'chargebackURL': '<this is not editable>',
        'postbackURL': '<this is not editable>',
        'defaultLocale': 'en',
        'locales': {
          'pl': {
            'name': 'Wirtualna Kiwi',
            'description': 'Zakazany owoc'
          }
        }
      }
    };
    if (server.simulate) {
      defaultJWT.request.simulate = server.simulate;
    }
    res.send(JSON.stringify(defaultJWT, null, 2));
  });

  app.get('/transaction/:trans', function (req, res) {
    var transID = req.params.trans;
    if (!config.db[transID]) {
      res.send(404);
      return;
    }
    res.send({state: config.db[transID].state,
              result: config.db[transID].result});
  });

  app.post('/pay', function (req, res) {
    var transID = uuid.v4();
    config.db[transID] = {state: 'pending', result: null};
    var jwtReq = JSON.parse(req.param('jwt'));
    console.log('pay with:', jwtReq);
    var server = config.servers[req.param('server')];
    if (!server) {
      console.log('/pay: server does not exist for', req.param('server'));
      res.send(400);
      return;
    }
    // WARNING! This will not work with concurrent users on the site.
    // mozpay needs a fix.
    pay.configure(server);

    // fill in non-editable fields.
    jwtReq.request.productData = qs.stringify({localTransID: transID}),
    jwtReq.request.postbackURL = config.postbackURL('postback');
    jwtReq.request.chargebackURL = config.postbackURL('chargeback');

    // WARNING:
    // In a real app you would *never* sign a JSON Web Token
    // that came entirely from user input (such as this textarea form).
    res.send({transID: transID,
              jwt: jwt.encode(jwtReq, server.mozPaySecret, 'HS256')});
  });

};

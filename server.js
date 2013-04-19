var express = require('express');

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
var media = __dirname + '/www';


var config = {
  host: '0.0.0.0',
  port: 3000,
  sessionSecret: 'set-this-in-local-settings',
  mozPayKey: null,
  mozPaySecret: null,
  mozPayAudience: 'marketplace.firefox.com',
  mozPayType: 'mozilla/payments/pay/v1',
  mozPayRoutePrefix: '/mozpay',
  // When not null, simulate this result instead of making a real purchase.
  simulate: null,

  addPort: function() {
    if (this.extPort) {
      return ':' + this.extPort;
    } else {
      return ''
    }
  },
  absURL: function(path) {
    return 'http://' + this.extHost + this.addPort() + (path || '');
  },
  postbackURL: function(path) {
     return this.absURL(this.mozPayRoutePrefix + '/' + path);
  },

  db: {}  // in-memory database!
};

config.extHost = config.host;
config.extPort = config.port;

localConfig(config);

config.manifestURL = config.absURL('/manifest.webapp');

app.configure(function() {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.set('view options', { layout: false });
  app.use(express.logger({format: 'dev'}));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(express.cookieParser());
  app.use(express.session({
    secret: config.sessionSecret
  }));
});

require("express-persona")(app, {
  audience: config.absURL()
});

require('./routes')(app, config);
require('./routes/payments')(app, config);

app.configure(function() {
  app.use(express.static(media));
});


app.listen(config.port, config.host);
console.log('Listening at ' + config.host + ':' + config.port);

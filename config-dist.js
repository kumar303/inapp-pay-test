module.exports = function(config) {
  // When not null, simulate this result instead of making a real purchase.
  config.simulate = {result: 'postback'};
  config.sessionSecret = 'set-this-to-something';

  // Basic support for Stackato PAAS.
  var isStackato = !!process.env.VCAP_APPLICATION;

  // Get payment keys from the Firefox Marketplace DevHub.
  if (isStackato) {
    // Production
    config.mozPayAudience = 'marketplace.firefox.com';
    config.mozPayType = 'mozilla/payments/pay/v1';
    config.mozPayKey = '...';
    config.mozPaySecret = '...';
    // Stage
    /*
    config.mozPayAudience = 'marketplace.allizom.org';
    config.mozPayType = 'mozilla-stage/payments/pay/v1';
    config.mozPayKey = '...';
    config.mozPaySecret = '...';
    */
    // Dev
    /*
    config.mozPayAudience = 'marketplace-dev.allizom.org';
    config.mozPayType = 'mozilla-dev/payments/pay/v1';
    config.mozPayKey = '...';
    config.mozPaySecret = '...';
    */
  } else {
    config.mozPayAudience = 'localhost';
    config.mozPayType = 'mozilla-local/payments/pay/v1';
    config.mozPayKey = '...';
    config.mozPaySecret = '...';
  }

  var app = isStackato
      ? JSON.parse(process.env.VCAP_APPLICATION)
      : {uris: [config.host]};
  // This is where your local server will run from.
  config.host = '0.0.0.0';
  config.port = process.env.VCAP_APP_PORT || 3000;
  // This is the URL your local host will be accessible from.
  config.extHost = app.uris[0];
  config.extPort = process.env.VCAP_APP_PORT ? null: config.port;
}

module.exports = function(config) {
  // When not null, simulate this result instead of making a real purchase.
  config.simulate = {result: 'postback'};
  config.sessionSecret = 'set-this-to-something';

  // Basic support for Stackato PAAS.
  var isStackato = !!process.env.VCAP_APPLICATION;

  // Get payment keys from the Firefox Marketplace DevHub.
  config.servers = [
    {name: 'marketplace.firefox.com (prod)',
     mozPayAudience: 'marketplace.firefox.com',
     mozPayType: 'mozilla/payments/pay/v1',
     mozPayKey: '...',
     mozPaySecret: '...'},
    {name: 'marketplace.firefox.com (prod, simulate only)',
     simulate: {result: 'postback'},
     mozPayAudience: 'marketplace.firefox.com',
     mozPayType: 'mozilla/payments/pay/v1',
     mozPayKey: '...',
     mozPaySecret: '...'},
    {name: 'marketplace.allizom.org (stage)',
     mozPayAudience: 'marketplace.allizom.org',
     mozPayType: 'mozilla-stage/payments/pay/v1',
     mozPayKey: '...',
     mozPaySecret: '...'},
    {name: 'marketplace-dev.allizom.org (dev)',
     mozPayAudience: 'marketplace-dev.allizom.org',
     mozPayType: 'mozilla-dev/payments/pay/v1',
     mozPayKey: '...',
     mozPaySecret: '...'},
  ];

  if (isStackato) {
    config.isSecure = true;
  } else {
    config.servers.push({
      name: 'fireplace.local',
      mozPayAudience: 'localhost',
      mozPayType: 'mozilla-local/payments/pay/v1',
      mozPayKey: '...',
      mozPaySecret: '...'
    });
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

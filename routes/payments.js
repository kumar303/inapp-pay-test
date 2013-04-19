var pay = require('mozpay');
var qs = require('qs');

module.exports = function(app, config) {

  pay.routes(app, config);

  function processData(data, done) {
    var transID = qs.parse(data.request.productData).localTransID;
    if (!config.db[transID]) {
      throw new Error('There is no record of transaction ' + transID);
    }
    if (config.db[transID].state == 'completed') {
      console.log('Transaction', transID, 'ignored.',
                  'Attacker may be trying to replay a JWT notice');
      done('already-processed');
      return;
    }
    console.log('transaction completed:', transID);
    config.db[transID].state = 'completed';
    done(null, config.db[transID]);
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

};

(function() {
  "use strict";

  function pay(done) {
    clearLog();
    showLog();
    writeLog('signing JWT...');

    function waitForResult(transID, opt) {
      opt = opt || {tries: 1};
      if (opt.tries > 10) {
        throw new Error('could not find transaction after 10 tries');
      }
      console.log('checking transaction', transID);
      $.get('/transaction/' + transID)
        .done(function(data, textStatus, jqXHR) {
          if (data.state == 'pending') {
            setTimeout(function() { waitForResult(transID, {tries: opt.tries + 1}) },
                       1000);
          } else {
            console.log('got result for transID', transID, data.state);
            if (data.state == 'completed') {
              done(null, data.result);
            } else {
              done('invalid completion state: ' + data.state);
            }
          }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
          console.log('error waiting for transaction:', textStatus, errorThrown);
        });
    }

    $.ajax({url: '/pay', type: 'post', cache: false,
            data: {jwt: $('#jwt-text').text()}})
      .done(function(data, textStatus, jqXHR) {
        writeLog('calling navigator.mozPay()...');
        var req = navigator.mozPay([data.jwt]);
        req.onsuccess = function() {
          writeLog('waiting for postback...');
          waitForResult(data.transID);
        };
        req.onerror = function() {
          done(this.error.name);
        }
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('error starting pay:', textStatus, errorThrown);
      });
  }

  function refresh() {
    showJWT();
    $.ajax({url: '/jwt-source', cache: false})
      .done(function(data, textStatus, jqXHR) {
        $('#jwt-text').text(data);
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('error getting catalog:', textStatus, errorThrown);
      });
  }

  function showLog() {
    $('#jwt-panel').hide();
    $('#log').show();
    $('#toggle').text('Show JWT');
  }

  function writeLog(msg) {
    var li = $('<li>' + msg + '</li>');
    $('#log ul').append(li);
  }

  function clearLog() {
    $('#log ul li').remove();
  }

  function showJWT() {
    $('#jwt-panel').show();
    $('#log').hide();
    $('#toggle').text('Show log');
  }

  function onReady() {
    refresh();
    $('#refresh').click(refresh);

    $('#pay').on('click', function() {
      pay(function(error, result) {
        if (error) {
          writeLog('error: ' + error);
          console.log('error with pay():', error);
        } else {
          writeLog('received: ' + result);
          console.log('payment result:', result);
        }
      });
    });

    $('#toggle').on('click', function() {
      if ($('#jwt-panel:visible').length) {
        showLog();
      } else {
        showJWT();
      }
    });
  }

  $(onReady);

})();

(function() {
  "use strict";

  $.fn.serializeObject = function() {
    /* returns a JS object */
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
      if (o[this.name] !== undefined) {
        if (!o[this.name].push) {
            o[this.name] = [o[this.name]];
        }
        o[this.name].push(this.value || '');
      } else {
        o[this.name] = this.value || '';
      }
    });
    return o;
  };

  function pay(form, done) {
    var editedJWT;
    // This is stupid. The textarea name attribute has a cache buster thing.
    for (var key in form) {
      if (key.slice(0, 3) == 'jwt') {
        editedJWT = form[key];
      }
    }
    if (!editedJWT) {
      console.error('could not get editedJWT');
    }
    console.log('jwt', editedJWT, 'server', form.server);
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

    console.log('edited JWT:', editedJWT);
    $.ajax({url: '/pay', type: 'post', cache: false,
            data: {jwt: editedJWT, server: form.server}})
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
    $.ajax({url: '/jwt-source', cache: false,
            data: {server: $('select#server').val()}})
      .done(function(data, textStatus, jqXHR) {
        console.log('refreshed JWT');
        // Replace textarea with brute force to prevent the browser from
        // trying to preserve any edits.
        $('#jwt-panel textarea').remove();
        var tx = $('<textarea>Loading...</textarea>');
        var id = Math.floor((Math.random() * 100) + 1);  // number between 1-100
        tx.attr('name', 'jwt' + id.toString());
        $('#jwt-panel').append(tx);
        tx.text(data);
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
    console.log(msg);
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

  function watch() {
    navigator.id.watch({
      onlogin: function(assertion) {
        $.post('/persona/verify', {assertion: assertion})
          .done(function(data, textStatus, jqXHR) {
            console.log('got verification');
            if (data && data.status === "okay") {
              console.log("You have been logged in as: " + data.email);
              $('#signin').hide();
              $('#signout button').text('Sign Out');
              $('#signout').show();
            }
          })
          .fail(function(jqXHR, textStatus, errorThrown) {
            console.log('error verifying assertion:', textStatus, errorThrown);
          });
      },
      onlogout: function() {
        $.post('/persona/logout')
          .done(function(data, textStatus, jqXHR) {
            console.log('logged out');
            $('#signout').hide();
            $('#signin button').text('Sign In');
            $('#signin').show();
          })
          .fail(function(jqXHR, textStatus, errorThrown) {
            console.log('error logging out:', textStatus, errorThrown);
          });
      },
      onready: function() {
        $('#signin button').text('Sign In');
      }
    });
  }

  function onReady() {
    refresh();
    $('#refresh').click(refresh);
    $('select#server').on('change', refresh);

    $('form#jwt-input').on('submit', function(evt) {
      evt.preventDefault();
      pay($(this).serializeObject(), function(error, result) {
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

    watch();

    $('#signin button').on('click', function() {
      navigator.id.request();
    });

    $('#signout button').on('click', function() {
      navigator.id.logout();
    });
  }

  $(onReady);

})();

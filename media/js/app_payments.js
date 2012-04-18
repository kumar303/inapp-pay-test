$(function() {
    'use strict';
    var localTransID, lastTransState;

    function consoleLog() {
        if (typeof console.log !== 'undefined') {
            console.log.apply(this, arguments);
        }
    }

    function log(msg) {
        // consoleLog(msg);
        var $log = $("#log pre");
        $log.show().html($log.html() + msg.toString() + "<br>");
    }

    function onBuySuccess() {
        log('mozmarket.buy() success!');
        log('watching for a postback/chargeback...');
        waitForTransChange();
    }

    function onBuyError() {
        log('mozmarket.buy() error!');
        $('#call-buy').removeClass('ajax-loading');
    }

    function waitForTransChange() {
        var state;
        $.ajax({
            url: '/en-US/check-trans',
            dataType: 'json',
            type: 'GET',
            data: {tx: localTransID},
            success: function(data) {
                if (data.mozTransactionID && data.transState != lastTransState) {
                    lastTransState = data.transState;
                    switch (data.transState) {
                        case 1:
                            state = 'pending';
                            break;
                        case 2:
                            log('received postback');
                            state = 'paid';
                            break;
                        case 3:
                            log('received chargeback');
                            state = 'reversed';
                            break;
                        default:
                            state = 'UNKNOWN';
                            break;
                    }
                    log('new transaction state: ' + state);
                }
                setTimeout(waitForTransChange, 5000);
                // $('#call-buy').removeClass('ajax-loading');
            },
            error: function(xhr, textStatus, errorThrown) {
                consoleLog('ERROR', xhr, textStatus, errorThrown);
            }
        });
    }

    $('#call-buy button').click(function(e) {
        e.preventDefault();
        $('#call-buy').addClass('ajax-loading');
        $('#pay-request').hide();
        $('#start-over').show();
        log("generating a signed JWT request...");
        $.ajax({
            url: '/en-US/sign-request',
            dataType: 'json',
            type: 'POST',
            data: $('#generator form').serialize(),
            success: function(data) {
                localTransID = data.localTransID;
                log('mozmarket.buy("' + data.signedRequest + '", onBuySuccess, onBuyError);');
                mozmarket.buy(data.signedRequest, onBuySuccess, onBuyError);
            },
            error: function(xhr, textStatus, errorThrown) {
                consoleLog('ERROR', xhr, textStatus, errorThrown);
            }
        });
    });

    $('#start-over').hide().click(function(e) {
        e.preventDefault();
        $('#pay-request').show();
        $('#start-over').hide();
        $("#log pre").text('').hide();
        $('#call-buy').removeClass('ajax-loading');
    });

});

$(function() {
    'use strict';
    var localTransID, lastTransState;

    function log(msg) {
        // console.log(msg);
        var $log = $("#log pre");
        $log.show().html($log.html() + msg.toString() + "<br>");
    }

    function onBuySuccess() {
        log('navigator.mozPay() success!');
        log('watching for a postback/chargeback...');
        waitForTransChange();
    }

    function onBuyError() {
        log('navigator.mozPay() error!');
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
                console.log('ERROR', xhr, textStatus, errorThrown);
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
            url: $('body').data('sign-url'),
            dataType: 'json',
            type: 'POST',
            data: $('#generator form').serialize(),
            success: function(data) {
                localTransID = data.localTransID;
                log('navigator.mozPay("' + data.signedRequest + '", onBuySuccess, onBuyError);');
                navigator.mozPay(data.signedRequest, onBuySuccess, onBuyError);
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log('ERROR', xhr, textStatus, errorThrown);
            }
        });
    });

});

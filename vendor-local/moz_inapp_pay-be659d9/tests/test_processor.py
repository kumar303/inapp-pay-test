import json

from nose.tools import eq_, raises

import moz_inapp_pay
from moz_inapp_pay import InvalidJWT

from . import JWTtester


class TestCallbacks(JWTtester):

    def setUp(self):
        super(TestCallbacks, self).setUp()

    def test_postback(self):
        payload = self.payload()
        data = self.verify(self.request(payload=json.dumps(payload)),
                           verifier=moz_inapp_pay.process_postback)
        eq_(data['response']['transactionID'],
            payload['response']['transactionID'])

    def test_chargeback(self):
        payload = self.payload(typ='mozilla/chargeback/pay/v1',
                               extra_res={'reason': 'refund'})
        data = self.verify(self.request(payload=json.dumps(payload)),
                           verifier=moz_inapp_pay.process_chargeback)
        eq_(data['response']['transactionID'],
            payload['response']['transactionID'])

    @raises(InvalidJWT)
    def test_chargeback_no_reason(self):
        payload = self.payload(typ='mozilla/chargeback/pay/v1')
        data = self.verify(self.request(payload=json.dumps(payload)),
                           verifier=moz_inapp_pay.process_chargeback)

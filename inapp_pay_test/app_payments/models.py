import urlparse

from django.dispatch import receiver
from django.db import models

import commonware.log
from moz_inapp_pay.djangoapp.signals import (moz_inapp_postback,
                                             moz_inapp_chargeback)
from tower import ugettext_lazy as _lazy


log = commonware.log.getLogger()


class ModelBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'created'


TRANS_PENDING = 1
TRANS_DONE = 2
TRANS_CHARGEBACK = 3
TRANS_STATE_CHOICES = {TRANS_PENDING: _lazy('pending'),
                       TRANS_DONE: _lazy('done'),
                       TRANS_DONE: _lazy('chargeback')}


class Transaction(ModelBase):
    moz_transaction_id = models.IntegerField(blank=True, null=True)
    product = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    state = models.IntegerField(choices=TRANS_STATE_CHOICES.items())


@receiver(moz_inapp_postback)
def mozmarket_postback(request, jwt_data, **kwargs):
    _change_trans_state(request, jwt_data, TRANS_DONE)


@receiver(moz_inapp_chargeback)
def mozmarket_chargeback(request, jwt_data, **kwargs):
    _change_trans_state(request, jwt_data, TRANS_CHARGEBACK)


def _change_trans_state(request, data, state):
    try:
        moz_trans_id = data['response']['transactionID']

        # e.g. transaction_id=1234
        pd = urlparse.parse_qs(data['request']['productdata'])
        trans = Transaction.objects.get(pk=pd['transaction_id'][0])
        trans.moz_transaction_id = moz_trans_id
        log.info('transaction %s changed from state %s to %s'
                 % (trans.pk, trans.state, state))
        trans.state = state
        trans.save()
    except:
        log.exception('Exception while processing request from %s'
                      % request.META.get('REMOTE_ADDR'))
        raise

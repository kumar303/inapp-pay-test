from django.db import models

from tower import ugettext_lazy as _lazy


class ModelBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'created'


TRANS_PENDING = 1
TRANS_DONE = 2
TRANS_STATE_CHOICES = {TRANS_PENDING: _lazy('pending'),
                       TRANS_DONE: _lazy('done')}


class Transaction(ModelBase):
    moz_transaction_id = models.IntegerField(blank=True, null=True)
    product = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    state = models.IntegerField(choices=TRANS_STATE_CHOICES.items())

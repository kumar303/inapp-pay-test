import django.dispatch


args = ['request', 'jwt_data']
moz_inapp_postback = django.dispatch.Signal(providing_args=args)
moz_inapp_chargeback = django.dispatch.Signal(providing_args=args)

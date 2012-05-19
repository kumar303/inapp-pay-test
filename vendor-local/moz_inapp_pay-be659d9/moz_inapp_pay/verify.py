import calendar
from datetime import datetime
import json
import sys
import time

import jwt

from .exc import InvalidJWT, RequestExpired


def verify_jwt(signed_request, key, secret,
               validators=[]):
    """
    Verifies a postback/chargeback JWT.

    Returns the trusted JSON data from the original request.
    JWT spec: http://openid.net/specs/draft-jones-json-web-token-07.html

    When there's an error, an exception derived from InvalidJWT
    will be raised.
    """
    try:
        signed_request = str(signed_request)  # must be base64 encoded bytes
    except UnicodeEncodeError, exc:
        _re_raise_as(InvalidJWT,
                     'Non-ascii payment JWT: %s' % exc)
    try:
        app_req = jwt.decode(signed_request, verify=False)
    except jwt.DecodeError, exc:
        _re_raise_as(InvalidJWT, 'Invalid payment JWT: %s' % exc)
    if not isinstance(app_req, dict):
        try:
            app_req = json.loads(app_req)
        except ValueError, exc:
            _re_raise_as(InvalidJWT,
                         'Invalid JSON for payment JWT: %s' % exc)

    # Check JWT issuer.
    issuer = app_req.get('iss', None)
    if not issuer:
        raise InvalidJWT('Payment JWT is missing iss (issuer)')

    # Check signature.
    try:
        jwt.decode(signed_request, secret, verify=True)
    except jwt.DecodeError, exc:
        _re_raise_as(InvalidJWT,
                     'Payment verification failed: %s' % exc,
                     issuer=issuer)

    # Check timestamps:
    try:
        expires = float(str(app_req.get('exp')))
        issued = float(str(app_req.get('iat')))
    except ValueError:
        _re_raise_as(InvalidJWT,
                     'Payment JWT had an invalid exp (%r) or iat (%r) '
                     % (app_req.get('exp'), app_req.get('iat')),
                     issuer=issuer)
    now = calendar.timegm(time.gmtime())
    if expires < now:
        raise RequestExpired('Payment JWT expired: %s UTC < %s UTC '
                             '(issued at %s UTC)'
                             % (datetime.utcfromtimestamp(expires),
                                datetime.utcfromtimestamp(now),
                                datetime.utcfromtimestamp(issued)),
                             issuer=issuer)
    if issued < (now - 3600):  # issued more than an hour ago
        raise RequestExpired('Payment JWT iat expired: %s UTC < %s UTC '
                             % (datetime.utcfromtimestamp(issued),
                                datetime.utcfromtimestamp(now)),
                             issuer=issuer)
    try:
        not_before = float(str(app_req.get('nbf')))
    except ValueError:
        app_req['nbf'] = None  # this field is optional
    else:
        about_now = now + 300  # pad 5 minutes for clock skew
        if not_before >= about_now:
            raise InvalidJWT('Payment JWT cannot be processed before '
                                 '%s UTC (nbf must be < %s UTC)'
                                 % (datetime.utcfromtimestamp(not_before),
                                    datetime.utcfromtimestamp(about_now)),
                                 issuer=issuer)

    # Check JWT audience.
    audience = app_req.get('aud', None)
    if not audience:
        raise InvalidJWT('Payment JWT is missing aud (audience)',
                             issuer=issuer)
    if audience != key:
        raise InvalidJWT('Payment JWT aud (audience) must be set to %r; '
                             'got: %r' % (key, audience),
                             issuer=issuer)

    # Check payment request.
    request = app_req.get('request', None)
    if not isinstance(request, dict):
        raise InvalidJWT('Payment JWT is missing request dict: %r'
                             % request, issuer=issuer)
    for key in ('price', 'currency', 'name', 'description'):
        if key not in request:
            raise InvalidJWT('Payment JWT is missing request[%r]'
                                 % key, issuer=issuer)

    # Check Mozilla Market reponse.
    response = app_req.get('response', None)
    if not isinstance(response, dict):
        raise InvalidJWT('Payment JWT is missing response dict: %r'
                             % request, issuer=issuer)
    for key in ('transactionID',):
        if key not in response:
            raise InvalidJWT('Payment JWT is missing response[%r]'
                                 % key, issuer=issuer)

    for vl in validators:
        vl(app_req)

    return app_req


def _re_raise_as(NewExc, *args, **kw):
    """Raise a new exception using the preserved traceback of the last one."""
    etype, val, tb = sys.exc_info()
    raise NewExc(*args, **kw), None, tb

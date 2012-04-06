import functools
import json

from django import http

import commonware

log = commonware.log.getLogger(__name__)


def post_required(view):
    @functools.wraps(view)
    def wrapper(request, *args, **kw):
        if request.method != 'POST':
            return http.HttpResponseNotAllowed(['POST'])
        else:
            return view(request, *args, **kw)
    return wrapper


def json_view(f=None, has_trans=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                response = func(*args, **kw)
                if isinstance(response, http.HttpResponse):
                    return response
                else:
                    if has_trans:
                        response = json.dumps(response, cls=json.JSONEncoder)
                    else:
                        response = json.dumps(response)
                    return http.HttpResponse(response,
                                             content_type='application/json')
            except:
                log.exception('Exception in @json_view')
                raise
        return wrapper
    if f:
        return decorator(f)
    else:
        return decorator

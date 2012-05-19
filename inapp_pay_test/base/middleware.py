import logging
import sys


log = logging.getLogger('playdoh')


class LogExceptionsMiddleware:

    def process_exception(self, request, exception):
        log.error('in %s' % request.path, exc_info=sys.exc_info())

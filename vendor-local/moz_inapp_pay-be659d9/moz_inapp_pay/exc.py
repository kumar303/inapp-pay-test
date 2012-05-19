__all__ = ['InvalidJWT', 'RequestExpired']


class InvalidJWT(Exception):
    """The JWT received by an issuer is invalid."""

    def __init__(self, msg, issuer=None):
        self.issuer = issuer
        if self.issuer:
            msg = '%s (iss=%r)' % (msg, self.issuer)
        super(Exception, self).__init__(msg)


class RequestExpired(InvalidJWT):
    """The JWT request expired."""

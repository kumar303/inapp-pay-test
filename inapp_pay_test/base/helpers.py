from django.conf import settings

from jingo import register


@register.filter
def absolutify(url, site=None):
    """Takes a URL and prepends the SITE_URL"""
    if url.startswith('http'):
        return url
    else:
        if site:
            return site + url
        return settings.SITE_URL + url

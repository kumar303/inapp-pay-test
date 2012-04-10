In-app Payment Tester
=====================

Requirements:

* Python 2.6 or greater
* swig (to build m2crypto)

Installation:

    git clone --recursive git://github.com/kumar303/inapp-pay-test.git
    cd inapp-pay-test
    virtualenv Env
    source Env/bin/activate
    pip install -r requirements/compiled.txt
    cp inapp_pay_test/settings/local.py-dist inapp_pay_test/settings/local.py
    python manage.py syncdb
    python manage.py runserver


In case you have trouble on Ubuntu with missing M2Crypto symbols, you may have
to install it from your package manager and re-build the env like this:

    sudo apt-get install python-m2crypto
    rm -fr Env
    virtualenv --system-site-packages Env
    ./Env/bin/pip install -r requirements/compiled.txt

Configuration
=============

To install the app, submit it to the Mozilla Marketplace (probably your local
version). This is the manifest URL:

    http://127.0.0.1:8000/manifest.webapp

Captain Obvious says choose the option called "premium app with in-app payments."
You'll come to a screen where you can set up the postback and chargeback URLs.

Postback URL:

    /en-US/postback

Chargeback URL:

    /en-US/chargeback

That will give you an application ID and an application secret.
Enter those in your `inapp_pay_test/settings/local.py` config, which is not
committed to git. Something like:

    APPLICATION_KEY = 'ZPLUZMDMUBIP9W687BWF'
    APPLICATION_SECRET = 'VpuV67JDd6Q6cvRhWMGW1K2ZHJSp0kicKs0gpF1qHVM'

Deployment
==========

Before deployment, you also need to run this:

    python manage.py compress_assets


To get your db set up in production, make sure the user of your web server
(e.g. www-data) owns the *root directory* of your code, then run something
like:

    sudo -u www-data python ./manage.py syncdb

Further Documentation
=====================

This app is built with [Playdoh](http://playdoh.readthedocs.org/),
a [Django](https://docs.djangoproject.com/) starter kit.

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/


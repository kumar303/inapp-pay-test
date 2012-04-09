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


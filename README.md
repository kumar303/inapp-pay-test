# In-app Payment Tester

This is an [open web app](https://developer.mozilla.org/en/Apps)
that implements Mozilla's
[navigator.mozPay() API](https://developer.mozilla.org/en/Apps/In-app_payments).
It is used for diagnostics / testing in the Marketplace development cycle.

## Run The App

You can run the app from
[http://inapp-pay-test.paas.allizom.org/](http://inapp-pay-test.paas.allizom.org/)
to test in-app payments.

## Customize It

If you want to customize the settings (like your payment keys) you can run the
app yourself almost as easily.

Requirements:

* NodeJS >= 0.8
* npm >= 1.1

Clone the source and install:

    git clone git://github.com/kumar303/inapp-pay-test.git
    cd inapp-pay-test
    npm install
    cp config-dist.js config.js

Edit `config.js` and enter your Application Key and Application Secret.
Start the development server:

    npm start

View the app at [http://0.0.0.0:3000/](http://0.0.0.0:3000/)
or install the manifest from
[http://0.0.0.0:3000/manifest.webapp](http://0.0.0.0:3000/manifest.webapp).

## Deployment

You can deploy to Mozilla's Stackato PAAS if you have access.
Edit the app name in `stackato.yml` so that it's unique across the cluster.
Create a new app like this:

    stackato push

Make updates:

    stackato update

You may want to edit `config.js` to set different settings while running in
Stackato.

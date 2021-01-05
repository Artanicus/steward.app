#!/usr/bin/env python3

__version__ = "0.0.2"

import sys
from absl import logging, flags
from flask import Flask, render_template, flash, redirect, request

from app.app_assets import assets
from app.extensions import lm, mail, bcrypt

from app.channels import Channels

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

FLAGS = flags.FLAGS
flags.DEFINE_string('sentry', None, 'Sentry endpoint')
FLAGS(sys.argv)

app = Flask(__name__)
app.config.from_object('websiteconfig')

if FLAGS.sentry:
    sentry_sdk.init(
        dsn=FLAGS.sentry,
        integrations=[FlaskIntegration()]
    )

assets.init_app(app)
lm.init_app(app)
mail.init_app(app)
bcrypt.init_app(app)

channels = Channels()
channels.resolve_all()

from app import user, maintenance, asset
app.register_blueprint(user.bp)
app.register_blueprint(maintenance.bp)
app.register_blueprint(asset.bp)

@app.route('/')
def root():
    return render_template('index.html')

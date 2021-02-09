# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging

import sentry_sdk
from sentry_sdk import set_level
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

from ckan import plugins

log = logging.getLogger(__name__)

CONFIG_FROM_ENV_VARS = {
    'sentry.dsn': 'CKAN_SENTRY_DSN',  # Alias for SENTRY_DSN, used by sentry_sdk
    'sentry.configure_logging': 'CKAN_SENTRY_CONFIGURE_LOGGING',
    'sentry.log_level': 'CKAN_SENTRY_LOG_LEVEL',
}


class SentryPlugin(plugins.SingletonPlugin):
    '''A simple plugin that add the Sentry middleware to CKAN'''
    plugins.implements(plugins.IMiddleware, inherit=True)

    def make_middleware(self, app, config):
        if plugins.toolkit.check_ckan_version('2.3'):
            return app
        else:
            return self.make_error_log_middleware(app, config)

    def make_error_log_middleware(self, app, config):

        for option in CONFIG_FROM_ENV_VARS:
            from_env = os.environ.get(CONFIG_FROM_ENV_VARS[option], None)
            if from_env:
                config[option] = from_env
        if not config.get('sentry.dsn') and os.environ.get('SENTRY_DSN'):
            config['sentry.dsn'] = os.environ['SENTRY_DSN']

        log.debug('Adding Sentry middleware...')
        sentry_sdk.init(dsn=config.get('sentry.dsn'))
        sentry_log_level = config.get('sentry.log_level', logging.INFO)
        set_level(sentry_log_level)

        log.debug('Setting up Sentry logger with level {0}'.format(
            sentry_log_level))

        sentry = SentryWsgiMiddleware(app)
        return app

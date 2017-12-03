#!/usr/bin/env python3.6

import json
import logging
import time
import sys
from urllib.parse import unquote

import falcon

import mconf_aggr.cfg as cfg
from mconf_aggr.event_listener import db_mapping
from mconf_aggr.event_listener.db_operations import DataWritter
from mconf_aggr.event_listener.event_listener import DataHandler, HookListener, AuthMiddleware
from mconf_aggr.aggregator import Aggregator, SetupError, PublishError

cfg.config.setup_config("config/config.json")
route = cfg.config['event_listener']['route']

# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=AuthMiddleware())

channel = "webhooks"
db_writter = DataWritter()

aggregator = Aggregator()
aggregator.register_callback(db_writter, channel=channel)

try:
    aggregator.setup()
except SetupError:
    sys.exit(1)

publisher = aggregator.publisher

data_handler = DataHandler(publisher, channel)
hook = HookListener(data_handler)
app.add_route(route, hook)

# when?
#aggregator.stop()
#db_reader.stop()

# hook will handle all requests to the self.route URL path

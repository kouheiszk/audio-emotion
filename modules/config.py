#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os

from IPython import embed


class Config(object):
    def __init__(self, config_file="config.json"):
        load = {}
        if os.path.isfile(config_file):
            with open(config_file) as data:
                load.update(json.load(data))

        embed()

        for key in config.__dict__:
            if key in load and config.__dict__[key] is None:
                self.__dict__[key] = str(load[key])

        self.__dict__.update(config.__dict__)


config = Config()

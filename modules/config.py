#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os


class Config(object):
    def __init__(self, config_file="config.json"):
        load = {}
        if os.path.isfile(config_file):
            with open(config_file) as data:
                load.update(json.load(data))

        self.__dict__.update(load)


config = Config()

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    config.py
# @Author:      kien.tadinh
# @Time:        5/4/2024 10:51 AM
import logging

import yaml


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(config_path, "r") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.Loader)
            self.CAMERAS = cfg.get('cameras')
            self.PORT = cfg['serial']['port']
            self.BAUD = cfg['serial']['baud']
            self.TIMEOUT = cfg['serial']['timeout']

    def config(self):
        return self.CAMERAS, self.PORT, self.BAUD, self.TIMEOUT

    # Setup logger
    def setup_logger(self):
        logging.basicConfig(
            filename='app.log',
            filemode='w',
            format='%(asctime)s - %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger(__name__)
        return logger
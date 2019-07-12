#!/usr/bin/env python3.6

import yaml,logbook,sys
from src.module01 import class01

class Run():

    def __init__(self):

        logbook.StreamHandler(sys.stdout).push_application()
        self.logger = logbook.Logger(__name__)
        logbook.set_datetime_format('local')

        with open('conf.yaml','r') as f:
            try:
                self.cfg = yaml.load(f)
            except Exception as error:
                self.logger.critical(f'Failed to open config file with {error}')
                sys.exit()

    def checkyaml(self):
        self.logger.debug(f'Config file reads {self.cfg}')


    def checkmodule01(self):
        statement = class01.function01(self)
        self.logger.debug(f'module01 reports {statement}')

if __name__ == '__main__':
    run = Run()
    run.checkyaml()
    run.checkmodule01()


#!/usr/bin/env python3

####################################################################################
#--------------------------------CX-ASAP: yaml_dumper------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#System Module ONLY 

#----------Required Modules----------#

import yaml
import logbook
import pathlib
import os

#----------Class Definition----------#

class Nice_YAML_Dumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        
        if len(self.indents) == 1:
            super().write_line_break()
            
        
class Config():
    def __init__(self, original_path = os.getcwd()):
        
        #Set up logbook and config file 
        
        logbook.FileHandler(original_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        self.conf_path = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent / 'conf.yaml'
        
        with open (self.conf_path, 'r') as f:
            try: 
                self.cfg = yaml.load(f, yaml.FullLoader)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
                

#!/usr/bin/env python3

####################################################################################
#----------------------------------CX-ASAP: xprep----------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

#This module will run XPREP automatically 

#----------Required Modules----------#

import os 
import yaml
import logbook
import pathlib
import subprocess
import re

#----------Class Definition----------#

class XPREP:  
    def __init__(self, location = 'temp', home_path = os.getcwd()):
        
        #Sets up the logbook - if being used in a pipeline, then the home_path can be pushed through, otherwise, the current working directory is taken to be the home_path
        
        #Ideally this will be a parameter in the sys_conf.yaml file, but you need the logbook established before reading in the .yaml file..... 
        
        logbook.FileHandler(home_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        #Finds the path of this module and uses the known directory tree of CX-ASAP to find the config file
    
        self.conf_path = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent / 'conf.yaml'
        
        with open (self.conf_path, 'r') as f:
            try: 
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
        if location == 'temp':
            os.chdir(self.cfg['analysis_path'])
                
        
    
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def run_xprep(self):
        
        #This function goes through all runs and runs xprep for a known structure 
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                os.chdir(run)
                xprep = subprocess.Popen(['xprep'], stdin = subprocess.PIPE, encoding='utf8')
                xprep.stdin.write(self.cfg['xprep_file_name'] + '\n')
                xprep.stdin.write('X\n')
                xprep.stdin.write('Y\n')
                xprep.stdin.write('P\n')
                xprep.stdin.write('U\n')
                xprep.stdin.write('O\n')
                xprep.stdin.write('1 0 0 0 1 0 0 0 1\n')
                xprep.stdin.write('S\n')
                xprep.stdin.write('I\n')
                xprep.stdin.write(self.cfg['space_group'] + '\n')
                xprep.stdin.write('Y\n')
                xprep.stdin.write('D\n')
                xprep.stdin.write('S\n')
                xprep.stdin.write('A\n')
                xprep.stdin.write('\n')
                xprep.stdin.write('E\n')
                xprep.stdin.write('C\n')
                xprep.stdin.write(self.cfg['chemical_formula'] + '\n')
                xprep.stdin.write('E\n')
                xprep.stdin.write('F\n')
                xprep.stdin.write('shelx\n')
                xprep.stdin.write('S\n')
                xprep.stdin.write('Y\n')
                xprep.stdin.write('\n')
                xprep.stdin.write('Q\n')
                xprep.stdin.close()
                xprep.wait()
                
                #checks to make sure xprep worked :)
                
                try:
                    file_size = os.stat('shelx.ins')
                except FileNotFoundError:
                    self.logger.info('Error - XPREP failed - structre ' + str(index + 1))
                else:
                    if file_size.st_size < 10:
                        self.logger.info('Error - INS file blank and XPREP failed - structure ' + str(index + 1))
                    else:
                        self.logger.info('Successfully created .ins file - structure ' + str(index + 1))
                    
                os.chdir('..')

#If the module is run independently, the class is initialised, and XPREP is run 
  
if __name__ == "__main__":
    cell_analysis = XPREP(os.getcwd())
    cell_analysis.run_xprep()

        
        
        
        



    




























    
    
    


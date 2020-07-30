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
        
        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
                
        #if location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['analysis_path'])
            
        os.chdir(location)
                
        
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
                xprep.stdin.write(self.cfg['User_Parameters_Full_Pipeline']['File_Names_And_Paths']['xprep_file_name'] + '\n')
                xprep.stdin.write('X\n')
                xprep.stdin.write('Y\n')
                xprep.stdin.write('P\n')
                xprep.stdin.write('U\n')
                xprep.stdin.write('O\n')
                xprep.stdin.write('1 0 0 0 1 0 0 0 1\n')
                xprep.stdin.write('S\n')
                xprep.stdin.write('I\n')
                xprep.stdin.write(self.cfg['System_Parameters']['space_group'] + '\n')
                xprep.stdin.write('Y\n')
                xprep.stdin.write('D\n')
                xprep.stdin.write('S\n')
                xprep.stdin.write('A\n')
                xprep.stdin.write('\n')
                xprep.stdin.write('E\n')
                xprep.stdin.write('C\n')
                xprep.stdin.write(self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['chemical_formula'] + '\n')
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
    from system.yaml_configuration import Config
    cell_analysis = XPREP(os.getcwd())
    cell_analysis.run_xprep()
else:
    from .system.yaml_configuration import Config
        
        
        
        



    




























    
    
    


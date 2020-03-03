#!/usr/bin/env python3

####################################################################################
#-----------------------------------CX-ASAP: xds-----------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

#This module will run XDS - yay! 

#----------Required Modules----------#

import os 
import yaml
import logbook
import pathlib
import subprocess
import re
import shutil
import fileinput

#----------Class Definition----------#

class XDS:  
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
                
    def sorted_properly(self,data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(data, key=alphanum_key)
    
    def change(self, parameter, new_value):
                    
        #Honestly I forget why this is so complicated, but I remember having a lot of problems so it is the way that it is *shrugs in code* 
                    
        flag = 0
        editing = '' 
        with open (self.cfg['XDS_INP_path'], 'rt') as in_file:
            for line in in_file:
                if parameter in line and flag == 0:
                    to_edit = line.split()[1:]
                    flag += 1
        for element in to_edit:
            editing += ' ' + str(element)
        edit = editing.strip(' ')
        flag = 0
        for line in fileinput.input(self.cfg['XDS_INP_path'], inplace = True):
            if parameter in line and flag == 0:
                line = line.rstrip('\r\n')    
                print(line.replace(edit, str(new_value)))
                flag += 1
            else:
                line = line.rstrip('\r\n')
                print(line)
    
    def reprocess (self):
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                #Makes a backup file, changes the name of the frames and copies it into the run folder
                
                shutil.copyfile(self.cfg['XDS_INP_path'], os.path.join(pathlib.Path(self.cfg['XDS_INP_path']).parent, 'temp.INP'))
                self.change('NAME_TEMPLATE_OF_DATA_FRAMES', 'img/' + run + '_??????.h5')
                os.chdir(run)
                shutil.copy(self.cfg['XDS_INP_path'], os.getcwd())
                os.remove(self.cfg['XDS_INP_path'])
                os.rename(os.path.join(pathlib.Path(self.cfg['XDS_INP_path']).parent, 'temp.INP'), self.cfg['XDS_INP_path'])
                
                #Removes any previous HKL files from the system to make sure that if XDS fails, then old data isn't being run through XPREP 
                
                for item in os.listdir():
                    if '.HKL' in item:
                        os.remove(item)
                        
                #Runs XDS 
                        
                os.system('xds_par')
                
                #Updates error log with what happened :) 
                
                for item in os.listdir():
                    if '.HKL' in item:
                        self.logger.info('Data successfully indexed and integrated - structure ' + str(index + 1))
                        
                os.chdir('..')
    
#If the module is run independently, the class is initialised, and XDS is run
  
if __name__ == "__main__":
    XDS = XDS(os.getcwd())
    XDS.reprocess()


        
        
        
        



    




























    
    
    


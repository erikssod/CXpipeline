#!/usr/bin/env python3

####################################################################################
#-------------------------------CX-ASAP: SHELXL_ref--------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

#This module will read and analyse all of the CIF files in the current folder and below in the directory tree

#If you would like a single CIF file analysed, place it in an otherwise empty folder

#If you would like multiple CIF files analysed, place all of them into a single folder or below in the directory tree 

#----------Required Modules----------#

import os 
import re
import yaml
import logbook
import pathlib
import subprocess
import shutil

#----------Class Definition----------#

class SHELXL:  
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
    
    def import_refinement(self, file_name):
        self.structure = []
        self.cell = []
        with open (self.cfg['ref_ins_path'], 'rt') as reference:
            structure = reference.readlines()
        for index, line in enumerate(structure):
            if index > 2:
                self.structure.append(line)
        with open (file_name, 'rt') as new_file:
            cell = new_file.readlines()
        for index, line in enumerate(cell):
            if index <= 2:
                self.cell.append(line)
        with open(file_name, 'w') as combined:
            for line in self.cell:
                combined.write(line)
            for line in self.structure:
                combined.write(line)
        
    def run_shelxl(self):
        
        #This function goes through all runs and runs xprep for a known structure 
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                os.chdir(run)
                for item in os.listdir():
                    if item.endswith('.ins'):
                        stem = pathlib.Path(item).stem
                        self.import_refinement(item)
                        weight = []
                        for m in range(0,10):
                            shelxl = subprocess.call(['shelxl', stem])
                            shutil.copy(stem + '.res', item)
                            with open (stem + '.res', 'rt') as refinement:
                                for line in refinement:
                                    if 'WGHT' in line:
                                        weight.append(line)
                            with open (item, 'rt') as initial:
                                lines = initial.readlines()
                            
                            ACTA_flag = 0
                            
                            for line in lines:
                                if 'ACTA' in line:
                                    ACTA_flag += 1
                                    
                            if ACTA_flag == 0:
                                    
                                with open (item, 'w') as initial:
                                    for line in lines:
                                        if 'FMAP' in line:
                                            initial.write('ACTA \n') 
                                            initial.write(line)
                                            
                                        if 'WGHT' in line:
                                            try: 
                                                initial.write(weight[1])
                                            
                                            except IndexError as error:
                                                self.logger.info(f'Refinement Unstable - {error}')
                                            
                                        else:
                                            initial.write(line)
                        
                        file_size = os.stat(item)
                        
                        if file_size.st_size < 1:
                            self.logger.info('Refinement failed - structure ' + str(index + 1))
                            try:
                                os.remove(stem + '.cif')
                                os.remove(stem + '.ins')
                                os.remove(stem + '.lst')
                            except FileNotFoundError:
                                pass
                        else:
                            self.logger.info('Refinement successful - structure ' + str(index + 1))
                    
                os.chdir('..')
        
    
        
    
#If the module is run independently, the class is initialised, the data is collected, and printed as a .csv file
  
if __name__ == "__main__":
    refinement = SHELXL(os.getcwd())
    refinement.run_shelxl()

        
        
        
        



    




























    
    
    


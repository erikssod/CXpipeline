#!/usr/bin/env python3

####################################################################################
#----------------------------CX-ASAP: additional_setup_vt--------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#Additional setup required for a VT Experiment 

#----------Required Modules----------#

import os 
import shutil
import yaml
import logbook
import pathlib
import re 
import pandas as pd
import math

#----------Class Definition----------#

class VT_Setup():
    def __init__(self, home_path = os.getcwd()):
        
        #Set up logbook and config file 
        
        logbook.FileHandler(home_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        self.conf_path = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent / 'conf.yaml'
        
        with open (self.conf_path, 'r') as f:
            try: 
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
                
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def Temperature_Collection(self):

        #This part of the code pulls all of the temperature parameters from the autoprocess.cif 

        if not os.path.exists(os.path.join(self.cfg['results_path'], 'Just Temps.csv')):

            os.chdir(self.cfg['analysis_path'])

            for run in self.sorted_properly(os.listdir()):
                try:
                    os.chdir(run)
                except NotADirectoryError:
                    pass
                else:
                    for files in os.listdir():
                        if 'autoprocess' in files:
                            with open (files, 'r') as cif_file:
                                lines = cif_file.readlines()
                                
                            with open(os.path.join(self.cfg['results_path'], 'temp_cif.cif'), 'a') as combined:
                                for line in lines:
                                    combined.write(line)
                                    
                        elif 'edited.cif' in files:
                            os.remove(files)
                        elif 'shelx.cif' in files:
                            os.remove(files)
                            
                            
                    os.chdir('..')
                
            os.chdir(self.cfg['results_path'])    

        
        data = {'_diffrn_ambient_temperature':[], '_diffrn_ambient_temperature_error': []}
        
        temp_cif_path = os.path.join(self.cfg['results_path'], 'temp_cif.cif')

        with open (temp_cif_path, 'rt') as f:
            for line in f:
                if '_diffrn_ambient_temperature' in line:
                    if '(' in line:
                        temp = line.strip('_diffrn_ambient_temperature').strip(' \n').split('(')
                        temp3 = temp[1].strip(')')
                        data['_diffrn_ambient_temperature'].append(float(temp[0]))
                        if '.' in line:
                            temp2 = temp[0].split('.')
                            data['_diffrn_ambient_temperature_error'].append(int(temp3)*10**-(int(len(temp2[1]))))
                        else:
                            data['_diffrn_ambient_temperature_error'].append(int(temp3))
                    else:
                        temp = line.strip('_diffrn_ambient_temperature').strip(' \n')
                        data['_diffrn_ambient_temperature'].append(float(temp))
                        data['_diffrn_ambient_temperature_error'].append(0)
        
        #Saves to a new .csv file which the program refers to at later points - if it already exists, won't make again 

        self.temp_df = pd.DataFrame(data)

        self.temp_df.to_csv('Just_Temps.csv', index = None)

        os.remove(os.path.join(self.cfg['results_path'], 'temp_cif.cif'))
        
    def Ref_Setup(self):
        #rewrites the ins file without the REM lines - to make things easier 
        
        good_lines = []
        cell_flag = 0
        good_index = 0
        
        with open (self.cfg['ref_ins_path'], 'rt') as ins_file:
            for index, line in enumerate(ins_file):
                if 'CELL' in line:
                    good_index = index
        with open (self.cfg['ref_ins_path'], 'rt') as ins_file:
            for index, line in enumerate(ins_file):
                if index == 0 or index >= good_index:
                    good_lines.append(line)
       
        with open (self.cfg['ref_ins_path'], 'w') as ins_file:
            for line in good_lines:
                ins_file.write(line)
                
        #Finds the space group and cell parameters of the reference structure and saves them to the config file 
                
        with open(self.cfg['ref_ins_path'], 'rt') as ins_file:
            split_line = []
            for line in ins_file:
                if 'CELL' in line:
                    split_line = line.split()
                elif 'TITL' in line:
                    self.cfg['space_group'] = line.split()[3]
                    
        ref_parameters = ['ref_INS_a', 'ref_INS_b', 'ref_INS_c', 'ref_INS_alpha', 'ref_INS_beta', 'ref_INS_gamma']
        
        for index, item in enumerate(ref_parameters):
            self.cfg[item] = float(split_line[index + 2])
                                              
        #Calculates the volume because it's not actually written anywhere 

        self.cfg['ref_INS_volume'] = self.cfg['ref_INS_a'] * self.cfg['ref_INS_b'] * self.cfg['ref_INS_c'] * math.sqrt(1 - (math.cos(self.cfg['ref_INS_alpha'] * (math.pi / 180)) ** 2) - (math.cos(self.cfg['ref_INS_beta'] * (math.pi / 180)) ** 2) - (math.cos(self.cfg['ref_INS_gamma'] * (math.pi / 180)) ** 2) + (2 * math.cos(self.cfg['ref_INS_alpha'] * (math.pi / 180)) * math.cos(self.cfg['ref_INS_beta'] * (math.pi / 180)) * math.cos(self.cfg['ref_INS_gamma'] * (math.pi / 180)))) 
        
        self.cfg['temps_already_in_cifs'] = 'no'
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f)
                  
#If the code is called individually from the commandline, the below code runs the required functions 
                    
if __name__ == "__main__":
    initialisation = VT_Setup()
    initialisation.Temperature_Collection()
    initialisation.Ref_Setup()
            
            
            
            
            

            







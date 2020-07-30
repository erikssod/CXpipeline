#!/usr/bin/env python3

####################################################################################
#-------------------------------CX-ASAP: SHELXL_ref--------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

#This module will refine a series of structures below in the directory tree based on a reference

#----------Required Modules----------#

import os 
import re
import yaml
import logbook
import pathlib
import subprocess
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import statistics 

#----------Class Definition----------#

class SHELXL:  
    def __init__(self, location = 'temp', home_path = os.getcwd()):
        
        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
                
        #if location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['analysis_path'])
        #else:
            #self.cfg['System_Parameters']['ref_ins_path'] = self.cfg['User_Parameters_Full_Pipeline']['File_Names_And_Paths']['reference_path']
            #with open (self.conf_path, 'w') as f:
                #yaml.dump(self.cfg, f, default_flow_style=False, Dumper=Nice_YAML_Dumper, sort_keys=False)
                
        os.chdir(location)
        if location == os.getcwd():
            self.cfg['System_Parameters']['ref_ins_path'] = self.cfg['User_Parameters_Full_Pipeline']['File_Names_And_Paths']['reference_path']
            with open (self.conf_path, 'w') as f:
                yaml.dump(self.cfg, f, default_flow_style=False, Dumper=Nice_YAML_Dumper, sort_keys=False)
                
                
    
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def import_refinement(self, file_name):
        
        with open (self.cfg['System_Parameters']['ref_ins_path'], 'rt') as reference:
            structure = reference.read()
        ref_x = re.search('LATT', structure)
        ref_y = re.search('END', structure)
        
        with open (file_name, 'rt') as new_file:
            cell = new_file.read()
        new_x = re.search('TITL', cell)
        new_y = re.search('LATT', cell)
        
        if new_x is None or new_y is None or ref_x is None or ref_y is None:
            if os.path.exists(reference_path) == True:
                pass
            else:
                self.logger.critical('.ins files of incorrect format')
                exit()
        else:
            complete_file = cell[new_x.start():new_y.start()] + structure[ref_x.start():ref_y.end()]
            
        with open(file_name, 'w') as combined:
            for line in complete_file:
                combined.write(line)
                
    def convergence_check(self, input_file, shift):
        convergence = False
        
        with open (input_file, 'rt') as refinement:
            lines = refinement.readlines()
            
        shift_param = []
        
        for line in lines:
            if 'Mean shift' in line:
                shift_param.append(line)
        
        for item in shift_param:
            shift.append(float(item.split(' ')[6]))

        if statistics.mean(shift[-int(self.cfg['User_Parameters_Full_Pipeline']['Refinement_Configuration']['refinements_to_check']):]) <= float(self.cfg['User_Parameters_Full_Pipeline']['Refinement_Configuration']['tolerance']):
            convergence = True
            self.logger.info('Refinement has converged')
        else:
            convergence = False
            self.logger.info('Refinement has not converged')
        
        return convergence, shift
        
    def run_shelxl(self, path = 'temp'):
        
        #This function goes through all runs and runs xprep for a known structure 
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                os.chdir(run)
                for item in os.listdir():
                    if item.endswith('.ins'):
                        stem = pathlib.Path(item).stem
                        self.import_refinement(item)
                        
                        df_weights = pd.DataFrame()
                        df_shifts = pd.DataFrame()
                        weight_list_1 = []
                        weight_list_2 = []
                        refinement_shifts = []
                        
                        convergence = False
                        refine_count = 0
                        while convergence == False and refine_count < 20:
                            refine_count += 1
                            weight = ''
                            shelxl = subprocess.call(['shelxl', stem])
                            shutil.copy(stem + '.res', item)
                            with open (stem + '.res', 'rt') as refinement:
                                lines = refinement.readlines()
                                end_flag = False
                                for line in lines:
                                    if end_flag == True and 'WGHT' in line:
                                        weight = line
                                        weight_list_1.append(float(line.split(' ')[6]))
                                        weight_list_2.append(float(line.split(' ')[12]))
                                    elif 'END' in line:
                                        end_flag = True
                                        
                            with open (item, 'rt') as initial:
                                lines = initial.readlines()
                            
                            self.logger.info(run)
                            self.logger.info(weight)
                            
                            ACTA_flag = False
                            
                            for line in lines:
                                if 'ACTA' in line:
                                    ACTA_flag = True
                                    
                            with open (item, 'w') as initial:
                                for line in lines:
                                    if 'WGHT' in line and ACTA_flag == False:
                                        initial.write('ACTA \n') 
                                        ACTA_flag = True
                                        initial.write(weight)
                                            
                                    elif 'WGHT' in line and ACTA_flag == True:
                                        initial.write(weight)
                                            
                                    else:
                                        initial.write(line)
                                        
                            if os.path.exists(stem + '.lst'):
                                convergence, refinement_shifts = self.convergence_check(stem + '.lst', refinement_shifts)
                            else:
                                continue
                        
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
       
                #Helps independence
        
                        current = os.getcwd()
        
                        if path == 'temp':
                            os.chdir(self.cfg['System_Parameters']['current_results_path'])
                        else:
                            os.chdir('..')
                    
                        x1 = list(range(1,len(weight_list_1) + 1))
                        x2 = list(range(1, len(refinement_shifts) + 1))
                        
                        y1a = weight_list_1
                        y1b = weight_list_2
                        y2 = refinement_shifts
                        
                        fig, (ax1, ax2) = plt.subplots(1, 2)
                        ax1.plot(x1, y1a, 'r', label = 'First Weight')
                        ax1.plot(x1, y1b, 'b', label = 'Second Weight')
                        xaxis = x1
                        yaxis1 = [float(i) for i in y1a]
                        yaxis2 = [float(i) for i in y1b]
                        ax1.set_title('Weighting Convergence - structure ' + str(index + 1))
                        ax1.set_xlabel('Refinement Cycle')
                        ax1.set_ylabel('Weight')
                        ax1.legend()
                        
                        ax2.plot(x2, y2, 'g')
                        xaxis = x2
                        yaxis = y2
                        ax2.set_title('Shift Convergence - structure ' + str(index + 1))
                        ax2.set_xlabel('Refinement Cycle')
                        ax2.set_ylabel('Shift')
                        
                        figure = plt.gcf()
                        figure.set_size_inches(16,12)
                        plt.savefig('Refinement_Statistics_' + str(index + 1) + '.png', bbox_inches = 'tight', dpi = 100)
                        plt.clf()
                        
                        os.chdir(current)
                        
                        
                os.chdir('..')
        
    
        
    
#If the module is run independently, the class is initialised, the data is collected, and printed as a .csv file
  
if __name__ == "__main__":
    from system.yaml_configuration import Nice_YAML_Dumper, Config
    refinement = SHELXL(os.getcwd())
    refinement.run_shelxl(os.getcwd())
else:
    from .system.yaml_configuration import Nice_YAML_Dumper, Config

        
        
        
        



    




























    
    
    


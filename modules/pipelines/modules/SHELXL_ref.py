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
import pandas as pd
import matplotlib.pyplot as plt

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
        
        with open (self.cfg['ref_ins_path'], 'rt') as reference:
            structure = reference.read()
        ref_x = re.search('LATT', structure)
        ref_y = re.search('END', structure)
        
        with open (file_name, 'rt') as new_file:
            cell = new_file.read()
        new_x = re.search('TITL', cell)
        new_y = re.search('LATT', cell)
        
        if new_x is None or new_y is None or ref_x is None or ref_y is None:
            pass
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
        
        self.logger.info('First Least Squares: ' + shift_param[0])
        self.logger.info('Last Least Squares: ' + shift_param[-1])
        
        first_shift = float(shift_param[0].split(' ')[6])
        last_shift = float(shift_param[-1].split(' ')[6])
        
        if last_shift == 0.000 and first_shift <= 0.003:
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
        
                        if path == 'temp':
                            os.chdir(self.cfg['current_results_path'])
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
                        
                        os.chdir(run)
                        
                        
                os.chdir('..')
        
    
        
    
#If the module is run independently, the class is initialised, the data is collected, and printed as a .csv file
  
if __name__ == "__main__":
    refinement = SHELXL(os.getcwd())
    refinement.run_shelxl(os.getcwd())

        
        
        
        



    




























    
    
    


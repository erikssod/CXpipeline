#!/usr/bin/env python3

####################################################################################
#-----------------------------CX-ASAP: rotation_planes-----------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

# This module finds and calculates the required rotation planes as defined in the config file   

#----------Required Modules----------#

import os 
import pandas as pd
import re
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import yaml
import logbook
import pathlib

#----------Class Definitions----------#

class Rotation_Planes:
    
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
            
        if len(self.cfg['reference_plane']) != 3:
            self.logger.critical('Reference plane in config file not understood by system')
    
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)

    def grab_cell(self, file_name):
        
        #collects the cell from that run to calculate the rotation against 
        
        with open(file_name, 'rt') as ins_file:
            split_line = []
            for line in ins_file:
                if 'CELL' in line:
                    split_line = line.split()
                        
        ref_parameters = ['ref_INS_a', 'ref_INS_b', 'ref_INS_c']
        
        self.ref_values = [0,0,0]
            
        for index, item in enumerate(ref_parameters):
            self.ref_values[index] = float(split_line[index + 2])
    
    def find_planes(self, file_name):
        
        #Finds the calculation in the .lst file 
        
        with open (file_name, 'rt') as lst_file:
            data = lst_file.readlines()
            
        index = 3
        flag = 0
        
        for line in data:
            if 'Least-squares planes' in line:
                plane = data[index]
                flag = 1
            index += 1
            
        data = []
        
        #signs do not matter = just make sure angle closest to the 0 instead of 180
        index = 0
            
        if flag == 1:
        
            for item in plane.split():
                try:
                    float(item)
                except ValueError:
                    pass
                else:
                    data.append(float(item))
                    
            #Calculates the difference in angle between atom plane and reference plane 
                    
            x = data[0] / self.ref_values[0]
            y = data[1] / self.ref_values[1]
            z = data[2] / self.ref_values[2]
            
            molecule_plane = [x, y, z]
            
            dot_product = molecule_plane[0] * self.cfg['reference_plane'][0] + molecule_plane[1] * self.cfg['reference_plane'][1] + molecule_plane[2] * self.cfg['reference_plane'][2]
            
            normal_molecule = math.sqrt((molecule_plane[0] ** 2) + (molecule_plane[1] ** 2) + (molecule_plane[2] ** 2))
            
            normal_reference = math.sqrt((self.cfg['reference_plane'][0] ** 2) + (self.cfg['reference_plane'][1] ** 2) + (self.cfg['reference_plane'][2] ** 2))
            
            angle = math.acos(dot_product / (normal_molecule * normal_reference)) * (180 / math.pi)
            
            if 180 - angle < 90:
                angle = 180 - angle
                
            return angle    
        
    def rotation_planes(self):
        
        #Cycles through and calcualtes the rotation planes 
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
                if os.path.isdir(run):
                    os.chdir(run)
                    for item in os.listdir():
                        if item.endswith('.lst'):
                            self.grab_cell(pathlib.Path(item).stem + '.ins')
                            rot_angle = self.find_planes(item)
                            
                            #Make new data frame each time and append to previous file 
                            
                            self.df = pd.DataFrame({'Test Number': self.cfg['process_counter'], 'Structure':[index + 1], 'Distance':[(index + 1) * int(self.cfg['mapping_step_size'])], 'Rotation Angle': [rot_angle]}) 
                            os.chdir(self.cfg['current_results_path'])
                            try:
                                old_data = pd.read_csv('rotation_angles.csv')
                            except FileNotFoundError:
                                self.df.to_csv('rotation_angles.csv', index = None)
                            else:
                                new_df = old_data.append(self.df)
                                new_df.to_csv('rotation_angles.csv', index = None)
                                
                    os.chdir(self.cfg['analysis_path'])
                            
        os.chdir(self.cfg['current_results_path'])
        
        full_data = pd.read_csv('rotation_angles.csv')
        
        #Separates teh data frames by the test number and plots the graphs 
        
        separated_by_test_dfs = []
        
        tests = list(dict.fromkeys(full_data['Test Number']))

        for item in tests:
            condition = full_data['Test Number'] == item
            separated_by_test_dfs.append(full_data[condition])
            
        index = 0
            
        for item in separated_by_test_dfs:
            item.to_csv(str(tests[index]) + '_rotation_angles.csv', index = None)
            
            x = item['Distance']
            angle = item['Rotation Angle']
            plt.scatter(x, angle, label = 'Angle')
            plt.xlabel('Distance($\mu$m)', fontsize = 12)
            plt.ylabel('Angle($^\circ$C)', fontsize = 12)
            plt.title(str(tests[index]) + ' Rotation Angles')
            plt.legend(fontsize = 12)
            
            figure = plt.gcf()
            figure.set_size_inches(16,12)
            
            plt.savefig(str(tests[index]) + '_rotation_angles.png', bbox_inches = 'tight', dpi = 100)
            plt.clf()
            
            index += 1


if __name__ == "__main__":
    analysis = Rotation_Planes(os.getcwd())
    analysis.rotation_planes()

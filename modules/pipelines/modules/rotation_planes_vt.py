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

        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
                
        #if location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['analysis_path'])
            
        os.chdir(location)
            
        self.ref_plane = []
        
        for item in self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['reference_plane']:
            if item.isdigit():
                self.ref_plane.append(int(item))
        
        if len(self.ref_plane) != 3:
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
            
            dot_product = molecule_plane[0] * self.ref_plane[0] + molecule_plane[1] * self.ref_plane[1] + molecule_plane[2] * self.ref_plane[2]
            
            normal_molecule = math.sqrt((molecule_plane[0] ** 2) + (molecule_plane[1] ** 2) + (molecule_plane[2] ** 2))
            
            normal_reference = math.sqrt((self.ref_plane[0] ** 2) + (self.ref_plane[1] ** 2) + (self.ref_plane[2] ** 2))
            
            angle = math.acos(dot_product / (normal_molecule * normal_reference)) * (180 / math.pi)
            
            if 180 - angle < 90:
                angle = 180 - angle
                
            return angle    
        
    def rotation_planes(self, path = 'temp'):
        
        #Helps independence
        
        if path == 'temp':
            analysis = self.cfg['System_Parameters']['analysis_path']
            results = self.cfg['System_Parameters']['current_results_path']
            temperatures = os.path.join(self.cfg['System_Parameters']['results_path'], 'Just_Temps.csv')
            temp_heading = '_diffrn_ambient_temperature'
        else:
            analysis = path
            results = path
            temperatures = self.cfg['Extra_User_Parameters_Individual_Modules']['temperature_path']
            temp_heading = self.cfg['Extra_User_Parameters_Individual_Modules']['temperature_heading']
        
        
        #Cycles through and calcualtes the rotation planes 
        
        index_2 = -1
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
                if os.path.isdir(run):
                    os.chdir(run)
                    for item in os.listdir():
                        if item.endswith('.lst'):
                            self.grab_cell(pathlib.Path(item).stem + '.ins')
                            rot_angle = self.find_planes(item)
                            
                            #Make new data frame each time and append to previous file 
                            temp_df = pd.read_csv(temperatures)
                            self.df = pd.DataFrame({'Structure':[index + 1], 'Temperature': temp_df.at[index_2, temp_heading], 'Rotation Angle': [rot_angle]}) 
                            os.chdir(results)
                            try:
                                old_data = pd.read_csv('rotation_angles.csv')
                            except FileNotFoundError:
                                self.df.to_csv('rotation_angles.csv', index = None)
                            else:
                                new_df = old_data.append(self.df)
                                new_df.to_csv('rotation_angles.csv', index = None)
                        if item == 'autoprocess.cif':
                            index_2 += 1
                                
                    os.chdir(analysis)
                        
        os.chdir(results)
        
        full_data = pd.read_csv('rotation_angles.csv')
        x = full_data['Temperature']
        angle = full_data['Rotation Angle']
        plt.scatter(x, angle, label = 'Angle')
        plt.xlabel('Temperature(K)', fontsize = 12)
        plt.ylabel('Angle($^\circ$C)', fontsize = 12)
        plt.title('Rotation Angles')
        plt.legend(fontsize = 12)
            
        figure = plt.gcf()
        figure.set_size_inches(16,12)
            
        plt.savefig('rotation_angles.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()


if __name__ == "__main__":
    from system.yaml_configuration import Nice_YAML_Dumper, Config
    analysis = Rotation_Planes(os.getcwd())
    analysis.rotation_planes(os.getcwd())
else:
    from .system.yaml_configuration import Nice_YAML_Dumper, Config

#!/usr/bin/env python3

####################################################################################
#-------------------------------CX-ASAP: cif_reading-------------------------------#
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
import pandas as pd
import re
import yaml
import logbook
import pathlib
from CifFile import ReadCif

#----------Class Definition----------#

class CIF_File:  
    def __init__(self, location = 'temp', home_path = os.getcwd()):
        
        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
                
        #if location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['current_results_path'])
        
        os.chdir(location)
                
        #Sets up empty lists/dictionaries to later populate with data        
        
        self.cif_files = []
        self.results = {}
        self.errors = {}
        self.structures_in_cif = []
        self.successful_positions = []
        
        #Sets these to 0 to reset from previous runs 
        
        self.cfg['System_Parameters']['Structures_in_each_CIF'] = self.structures_in_cif
        self.cfg['System_Parameters']['Successful_Positions'] = self.successful_positions
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f, default_flow_style=False, Dumper=Nice_YAML_Dumper, sort_keys=False)
        
        #Pulls parameters from the configuration file as necessary, and uses it to set up an empty dataframe
        
        self.search_items = self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['cell_parameters']
        
        for item in self.search_items:
            self.results[item] = []
            self.errors[item] = []
        self.data = pd.DataFrame() 
        self.temp_df = pd.DataFrame()
        self.data2 = pd.DataFrame()
        self.data3 = pd.DataFrame()
        self.data4 = pd.DataFrame()
        
    
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def get_data(self):
        
        #This function searches through all of the folders in the current working directory for a cif file
        
        for dirName, subdirList, fileList in os.walk(os.getcwd()):
            sorted_fileList = self.sorted_properly(fileList)
            for files in sorted_fileList:
                
                #Once a unique CIF file is identified (checks for duplicates), the name is appended to a list and the data_harvest function is run on it 

                if files.endswith('.cif') and files.lower() not in self.cif_files:
                    self.cif_files.append(files.lower())
                    self.logger.info(files)
                    cif_file = os.path.join(os.getcwd(), files)
                    
                        
                    temp_data, structures_in_cif_tmp, successful_positions_tmp, temp_bonds, temp_angles, temp_torsion = self.data_harvest(cif_file)
                    
                    self.data = self.data.append(temp_data)
                    self.data2 = self.data2.append(temp_bonds)
                    self.data3 = self.data3.append(temp_angles)
                    self.data4 = self.data4.append(temp_torsion)
                    self.structures_in_cif.append(structures_in_cif_tmp)
                        
                    for item in successful_positions_tmp:
                        self.successful_positions.append(item)
                    
        self.cfg['System_Parameters']['Structures_in_each_CIF'] = self.structures_in_cif
        self.cfg['System_Parameters']['Successful_Positions'] = self.successful_positions
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f, default_flow_style=False, Dumper=Nice_YAML_Dumper, sort_keys=False)

        return self.data, self.data2
                    
                    
    def parameter_tidy(self, raw, item):
        if '(' in raw:
            temp = raw.split('(')
            temp2 = temp[1].strip(')')
            self.results[item].append(float(temp[0]))
            if '.' in raw:
                temp3 = temp[0].split('.')
                self.errors[item].append(int(temp2)*10**-(int(len(temp3[1]))))
            else:
                self.errors[item].append(int(temp2))
        else:
            try:
                self.results[item].append(float(raw))
            except ValueError:
                self.results[item].append(raw)
            self.errors[item].append(0)
        
    
    def generate_cif_list(self, df):
        longer_cif_list = []
        longer_data_blocks = []
        if len(df) != 0:
            for item in self.cif_list:
                i = 0
                while i < (len(df) / len(self.cif_list)):
                    longer_cif_list.append(item)
                    i += 1
            for item in self.data_blocks:
                i = 0
                while i < (len(df) / len(self.data_blocks)):
                    longer_data_blocks.append(item)
                    i += 1
        return longer_cif_list, longer_data_blocks
    
    def data_harvest(self, cif_file):                
                    
        #Resets the dataframes/dictionaries            
                    
        for item in self.search_items:
            self.results[item] = []
            self.errors[item] = []
        self.temp_df = pd.DataFrame()
        self.bond_df = pd.DataFrame()
        self.angle_df = pd.DataFrame()
        self.torsion_df = pd.DataFrame()
        
        #This notation is from the CifFile module and allows for easy searching of parameters
        
        cif = ReadCif(cif_file)
        
        #Identifies datablocks within the CIF file
        
        self.data_blocks = []
        
        with open (cif_file, 'rt') as f:
            for line in f:
                if line.startswith('data_'):
                    self.data_blocks.append(line.strip('\n').strip('data_'))
                    
        number_of_structures = len(self.data_blocks)
        
                
        #For each search item in the config file, the cif file is searched 
        
        for item in self.search_items:
            self.logger.info('File ' + pathlib.Path(cif_file.lower()).stem + ' opened. Searching for parameter ' + item)
            
            #This parameter is blanked every loop because each cif is searched multiple times
            
            self.cif_list = []
            
            #Since the CifFile module works by looking at data-blocks, use the found list of data blocks to search through the CIF
            
            for experiment in self.data_blocks:
                try:
                    raw = cif[experiment][item]
                except:
                    self.logger.critical('Failed to find ' + item + ' in ' + pathlib.Path(cif_file.lower()).stem)
                    exit()
                
                self.logger.info('File ' + pathlib.Path(cif_file.lower()).stem + ' - found parameter ' + item)
                self.cif_list.append(pathlib.Path(cif_file.lower()).stem)
                
                #Check if an error value is present and separates the value and the error, converts the error to the correct decimal point, and assigns an error of 0 if no error present 
                
                if type(raw) != list:
                    self.parameter_tidy(raw, item)
                else:
                    for param in raw:
                        self.parameter_tidy(param, item)
         
        #Creates a column in the data frame to include the file name of the CIF
        
        self.temp_df['CIF File'] = self.cif_list
        
        #Adds all of the data to one data frame 
        
        bond_paras = ['_geom_bond_atom_site_label_1', '_geom_bond_atom_site_label_2', '_geom_bond_distance']
        angle_paras = ['_geom_angle_atom_site_label_1', '_geom_angle_atom_site_label_2', '_geom_angle_atom_site_label_3', '_geom_angle']
        torsion_paras = ['_geom_torsion_atom_site_label_1', '_geom_torsion_atom_site_label_2', '_geom_torsion_atom_site_label_3', '_geom_torsion_atom_site_label_4', '_geom_torsion']
   
        for para in self.search_items:
            if len(self.results[para]) == len(self.cif_list):
                self.temp_df[para] = self.results[para]
                self.temp_df[para + '_error'] = self.errors[para]
            elif len(self.results[para]) != 0 and para in bond_paras:
                self.bond_df[para] = self.results[para]
                self.bond_df[para + '_error'] = self.errors[para]
            elif len(self.results[para]) != 0 and para in angle_paras:
                self.angle_df[para] = self.results[para]
                self.angle_df[para + '_error'] = self.errors[para]
            elif len(self.results[para]) != 0 and para in torsion_paras:
                self.torsion_df[para] = self.results[para]
                self.torsion_df[para + '_error'] = self.errors[para]
        
        
        self.bond_df['Cif File'], self.bond_df['Data Block'] = self.generate_cif_list(self.bond_df)
        self.angle_df['Cif File'], self.angle_df['Data Block'] = self.generate_cif_list(self.angle_df)
        self.torsion_df['Cif File'], self.torsion_df['Data Block'] = self.generate_cif_list(self.torsion_df)
        
        return self.temp_df, number_of_structures, self.data_blocks, self.bond_df, self.angle_df, self.torsion_df
    
    def data_output(self):
        self.data.to_csv('CIF_Parameters.csv', index = None)
        self.data2.to_csv('Bond_Lengths.csv', index = None)
        self.data3.to_csv('Bond_Angles.csv', index = None)
        self.data4.to_csv('Bond_Torsions.csv', index = None)
        
    
#If the module is run independently, the class is initialised, the data is collected, and printed as a .csv file
  
if __name__ == "__main__":
    from system.yaml_configuration import Nice_YAML_Dumper, Config
    analysis = CIF_File(os.getcwd())
    data = analysis.get_data()
    analysis.data_output()
else: 
    from .system.yaml_configuration import Nice_YAML_Dumper, Config


#!/usr/bin/env python3

####################################################################################
#-------------------------------CX-ASAP: cif_compile-------------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

      
#----------Instructions for Use----------#

# This module will compile cifs into one big happy cif 

#----------Required Modules----------#

import os 
import re
import yaml
import logbook
import pathlib
from CifFile import ReadCif
import pandas as pd

#----------Class Definition----------#

class CIF_Combine:  
    def __init__(self, location = 'temp', home_path = os.getcwd()):
        
        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
        
        self.location = location
        
        #if self.location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['analysis_path'])
            
        os.chdir(location)
    
    def sorted_properly(self, data):
        
        #This function sorts the files/folders properly (ie going 0, 1, 2... 10 instead of 0, 1, 10, 2... etc)
        
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def datablock_naming(self, file_name, index):
        
        #Names the datablocks to distinguish the datablocks in the cifs 
        
        with open (file_name, 'rt') as cif:
            name = []
            lines = cif.readlines()
        for line in lines:
            if 'data_' + pathlib.Path(file_name).stem in line:
                
                name.append(line.split('_')[0] + '_' + str(index + 1))
                
                #name.append(line.strip('\n').strip(pathlib.Path(file_name).stem) + str(index + 1))

        with open (file_name, 'w') as cif:
            for line in lines:
                if 'data_' + pathlib.Path(file_name).stem in line:
                    cif.write(name[0])
                else:
                    cif.write(line)
                        
    def finalise_parameters(self, file_name, index, current_temp):
        
        #Finalises the CIF with important parameters such as beamline parameters 
        
        cif = ReadCif(file_name)
        
        try:
            data_block = cif[str(index + 1)]
        except TypeError as error:
            os.remove(file_name)
            self.logger.info(f'Cif empty due to poor refinement - {error}')
        else:
            
            self.C = data_block['_diffrn_reflns_number']
            self.A = data_block['_diffrn_reflns_theta_min']
            self.B = data_block['_diffrn_reflns_theta_max']
            
            beamline = self.cfg['User_Parameters_Full_Pipeline']['Experiment_Configuration']['beamline']
            
            if beamline != '':
            
                data_block['_computing_data_collection'] = self.cfg['Instrument_Parameters'][beamline +'_data_collection']
                data_block['_exptl_absorp_correction_type'] = self.cfg['Instrument_Parameters'][beamline +'_absorp_correction']
                data_block['_diffrn_radiation_wavelength'] = self.cfg['User_Parameters_Full_Pipeline']['Experiment_Configuration']['wavelength']
                data_block['_diffrn_radiation_type'] = self.cfg['Instrument_Parameters'][beamline +'_radiation_type']
                data_block['_diffrn_source'] = self.cfg['Instrument_Parameters'][beamline +'_radiation_type']
                data_block['_diffrn_measurement_device_type'] = self.cfg['Instrument_Parameters'][beamline +'_detector']
                data_block['_diffrn_measurement_method'] = self.cfg['Instrument_Parameters'][beamline +'_measurement_method']
                data_block['_computing_cell_refinement'] = self.cfg['Instrument_Parameters'][beamline +'_cell_refinement']
                data_block['_computing_data_reduction'] = self.cfg['Instrument_Parameters'][beamline +'_cell_refinement']
                data_block['_computing_structure_solution'] = self.cfg['Instrument_Parameters'][beamline +'_structure_soln']
                data_block['_diffrn_radiation_monochromator'] = self.cfg['Instrument_Parameters'][beamline +'_monochromator']
                data_block['_diffrn_radiation_source'] = self.cfg['Instrument_Parameters'][beamline +'_source']
            
            data_block['_chemical_formula_moiety'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['chemical_formula']
            data_block['_exptl_crystal_colour'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['crystal_colour']
            data_block['_exptl_crystal_description'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['crystal_habit']
            data_block['_cell_measurement_temperature'] = current_temp
            data_block['_diffrn_ambient_temperature'] = current_temp
            data_block['_exptl_crystal_size_max'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['max_crystal_dimension']
            data_block['_exptl_crystal_size_mid'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['middle_crystal_dimension']
            data_block['_exptl_crystal_size_min'] = self.cfg['User_Parameters_Full_Pipeline']['Crystal_Descriptions']['min_crystal_dimension']
            data_block['_cell_measurement_reflns_used'] = self.C
            data_block['_cell_measurement_theta_min'] = self.A
            data_block['_cell_measurement_theta_max'] = self.B
            
            with open ('edited.cif', 'w') as updated:
                updated.write(cif.WriteOut())
                
            os.rename('edited.cif', file_name)
            
    def combine(self):
        
        #This function compiles the cifs into one place and runs the previous two functions 
        
        index_2 = 0
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                os.chdir(run)
                for item in self.sorted_properly(os.listdir()):
                    if item.endswith('.cif') and 'autoprocess' not in item:

                        if self.location == 'temp': 
                            temperatures = os.path.join(self.cfg['System_Parameters']['results_path'], 'Just_Temps.csv')
                            temp_heading = '_diffrn_ambient_temperature'
                        else:
                            temperatures = self.cfg['Extra_User_Parameters_Individual_Modules']['temperature_path']
                            temp_heading = self.cfg['Extra_User_Parameters_Individual_Modules']['temperature_heading']
                            
                        temp_df = pd.read_csv(temperatures)
                        current_temp = temp_df.at[index_2, temp_heading]
                        
                        self.datablock_naming(item,index)
                        self.finalise_parameters(item, index, current_temp)
                        
                        if self.location == 'temp':
                            with open (os.path.join(self.cfg['System_Parameters']['current_results_path'], '_all_cifs.cif'), 'a') as combined_cif:
                                try:
                                    with open (item) as single_cif:
                                        combined_cif.write(single_cif.read())
                                except FileNotFoundError as error:
                                    self.logger.info('Stuff messed up :(')
                        else:
                            with open (os.path.join(self.location, 'all_cifs.cif'), 'a') as combined_cif:
                                try:
                                    with open (item) as single_cif:
                                        combined_cif.write(single_cif.read())
                                except FileNotFoundError as error:
                                    self.logger.info('Stuff messed up :(')
                    if item == 'autoprocess.cif':
                        index_2 += 1
                        
                os.chdir('..')
    
#If the module is run independently, the class is initialised,and the cifs are compiled 
  
if __name__ == "__main__":
    from system.yaml_configuration import Nice_YAML_Dumper, Config
    combine = CIF_Combine(os.getcwd())
    combine.combine()
else:
    from .system.yaml_configuration import Nice_YAML_Dumper, Config


        











    
    
    


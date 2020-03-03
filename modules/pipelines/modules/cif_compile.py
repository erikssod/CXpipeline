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

#----------Class Definition----------#

class CIF_Combine:  
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
    
    def datablock_naming(self, file_name, index):
        
        #Names the datablocks to distinguish the datablocks in the cifs 
        
        with open (file_name, 'rt') as cif:
            name = []
            lines = cif.readlines()
        for line in lines:
            if 'data_' + pathlib.Path(file_name).stem in line:
                name.append(line.strip('\n').strip(pathlib.Path(file_name).stem) + str(index + 1))
        with open (file_name, 'w') as cif:
            for line in lines:
                if 'data_' + pathlib.Path(file_name).stem in line:
                    cif.write(name[0])
                else:
                    cif.write(line)
                        
    def finalise_parameters(self, file_name, index):
        
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
            
            beamline = self.cfg['beamline']
            
            if beamline != '':
            
                data_block['_computing_data_collection'] = self.cfg[beamline +'_data_collection']
                data_block['_exptl_absorp_correction_type'] = self.cfg[beamline +'_absorp_correction']
                data_block['_diffrn_radiation_wavelength'] = self.cfg['wavelength']
                data_block['_diffrn_radiation_type'] = self.cfg[beamline +'_radiation_type']
                data_block['_diffrn_source'] = self.cfg[beamline +'_radiation_type']
                data_block['_diffrn_measurement_device_type'] = self.cfg[beamline +'_detector']
                data_block['_diffrn_measurement_method'] = self.cfg[beamline +'_measurement_method']
                data_block['_computing_cell_refinement'] = self.cfg[beamline +'_cell_refinement']
                data_block['_computing_data_reduction'] = self.cfg[beamline +'_cell_refinement']
                data_block['_computing_structure_solution'] = self.cfg[beamline +'_structure_soln']
                data_block['_diffrn_radiation_monochromator'] = self.cfg[beamline +'_monochromator']
                data_block['_diffrn_radiation_source'] = self.cfg[beamline +'_source']
            
            data_block['_chemical_formula_moiety'] = self.cfg['chemical_formula']
            data_block['_exptl_crystal_colour'] = self.cfg['crystal_colour']
            data_block['_exptl_crystal_description'] = self.cfg['crystal_habit']
            data_block['_cell_measurement_temperature'] = self.cfg['temp']
            data_block['_diffrn_ambient_temperature'] = self.cfg['temp']
            data_block['_exptl_crystal_size_max'] = self.cfg['max_crystal_dimension']
            data_block['_exptl_crystal_size_mid'] = self.cfg['middle_crystal_dimension']
            data_block['_exptl_crystal_size_min'] = self.cfg['min_crystal_dimension']
            data_block['_cell_measurement_reflns_used'] = self.C
            data_block['_cell_measurement_theta_min'] = self.A
            data_block['_cell_measurement_theta_max'] = self.B
            
            with open ('edited.cif', 'w') as updated:
                updated.write(cif.WriteOut())
                
            os.rename('edited.cif', file_name)
            
    def combine(self):
        
        #This function compiles the cifs into one place and runs the previous two functions 
        
        for index, run in enumerate(self.sorted_properly(os.listdir())):
            if os.path.isdir(run):
                os.chdir(run)
                for item in os.listdir():
                    if item.endswith('.cif') and 'autoprocess' not in item:
                        self.datablock_naming(item,index)
                        self.finalise_parameters(item, index)
                        with open (os.path.join(self.cfg['current_results_path'], str(self.cfg['process_counter']) + '_all_cifs.cif'), 'a') as combined_cif:
                            try:
                                with open (item) as single_cif:
                                    combined_cif.write(single_cif.read())
                            except FileNotFoundError as error:
                                self.logger.info('Stuff messed up :(')
                os.chdir('..')
    
#If the module is run independently, the class is initialised,and the cifs are compiled 
  
if __name__ == "__main__":
    combine = CIF_Combine(os.getcwd())
    combine.combine()


        











    
    
    


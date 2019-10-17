#!/usr/bin/env python3


       
#----------Required Modules----------#


import os 
import shutil
import subprocess
#import pandas as pd
import math
import fileinput
import re
from CifFile import ReadCif
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
#import logging
import yaml
import logbook
import sys 


#----------Class Definitions----------#
                
class INS_File:
    
    #The INS_File class finds all cell parameters and saves them to a property of the object - also has the ability to add lines to the INS file

    def __init__(self, path_to_self, home_path):
        logbook.FileHandler(home_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        with open('/usr/local/bin/scripts/conf.yaml', 'r') as f:
            try:
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
        #Sets up the INS file - removing bad lines and adding in important ones (like ACTA)
        
        self.path = path_to_self
        good_lines = []
        with open (self.path, 'rt') as ins_file:
            for line in ins_file:
                if 'REM' not in line:
                    good_lines.append(line)
        with open (self.path, 'w') as ins_file:
            for line in good_lines:
                ins_file.write(line)
                
        with open (self.path, 'rt') as ins_file:
            split_line = []
            for line in ins_file:
                if 'CELL' in line:
                    split_line = line.split()
                elif 'TITL' in line:
                    self.space_group = line.split()[3]
                    
        self.a = float(split_line[2])
        self.b = float(split_line[3])
        self.c = float(split_line[4])
        self.alpha = float(split_line[5])
        self.beta = float(split_line[6])
        self.gamma = float(split_line[7])
        self.volume = self.a * self.b * self.c * math.sqrt(1 - (math.cos(self.alpha * (math.pi / 180)) ** 2) - (math.cos(self.beta * (math.pi / 180)) ** 2) - (math.cos(self.gamma * (math.pi / 180)) ** 2) + (2 * math.cos(self.alpha * (math.pi / 180)) * math.cos(self.beta * (math.pi / 180)) * math.cos(self.gamma * (math.pi / 180))))
        
        try:
            self.add_line('ACTA')
        except:
            self.logger.critical('Failed to add ACTA command to .ins')
            exit()
    
    def add_line(self, parameter):
        with open (self.path, 'rt') as ins_file:
            lines = ins_file.readlines()
        with open (self.path, 'w') as ins_file:
            for line in lines:
                if 'FVAR' not in line:
                    ins_file.write(line)
                else:
                    ins_file.write(parameter + '\n')
                    ins_file.write(line)

    def __repr__(self):
        return "Crystallographic Instruction File"
    
class Reference_INS(INS_File):
    
    #A subclass which saves the structure part of the ins so that it can be 'pasted' into new ins files to refine against

    def __init__(self, path, home_path):
        super().__init__(path, home_path)
        line_no = 1
        self.structure = []
        with open (self.path, 'rt') as reference:
            structure = reference.readlines()
        for line in structure:
            if line_no > 3:
                self.structure.append(line)
            line_no += 1
    
    def __repr__(self):
        return "Reference .ins file"
    
class New_INS(INS_File):
    
    #A subclass which saves the cell part of the ins and imports the structure from a reference 

    def __init__(self, path, home_path):
        super().__init__(path, home_path)
        line_no = 1
        self.cell = []
        with open (self.path, 'rt') as new_file:
            cell = new_file.readlines()
        for line in cell:
            if line_no <= 3:
                self.cell.append(line)
            line_no += 1
            
    def import_refinement(self, ref_object):
        with open ('shelx.ins', 'w') as structure:
            for line in self.cell:
                structure.write(line)
            for line in ref_object.structure:
                structure.write(line)
            
    def __repr__(self):
        return "New .ins file"
    
    
class CIF_File():
    
    def __init__(self, path_to_self, home_path):
        logbook.FileHandler(home_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        with open('/usr/local/bin/scripts/conf.yaml', 'r') as f:
            try:
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
        
        self.path = path_to_self
        
    def Datablock_Naming(self,counter):
        with open (self.path, 'rt') as cif:
            name = []
            lines = cif.readlines()
        for line in lines:
            if 'data_shelx' in line:
                name.append(line.strip('\n').strip('shelx') + str(counter))
        with open (self.path, 'w') as cif:
            for line in lines:
                if 'data_shelx' in line:
                    cif.write(name[0])
                else:
                    cif.write(line)
        
    def Finalisation_Parameters(self,counter, filenames, data_worked):
        
        cif = ReadCif('shelx.cif')
        
        try:
        
            data_block = cif[str(counter)]
        except TypeError as error:
            os.remove('shelx.cif')
            self.logger.info(f'Cif empty due to poor refinement - {error}')
            
        else:
            
            self.C = data_block['_diffrn_reflns_number']
            self.A = data_block['_diffrn_reflns_theta_min']
            self.B = data_block['_diffrn_reflns_theta_max']
            
            beamline = self.cfg['beamline']
            
            data_block['_chemical_formula_moiety'] = self.cfg['chemical_formula']
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
            data_block['_exptl_crystal_colour'] = self.cfg['crystal_colour']
            data_block['_exptl_crystal_description'] = self.cfg['crystal_habit']
            data_block['_cell_measurement_temperature'] = self.cfg['temp']
            data_block['_diffrn_ambient_temperature'] = self.cfg['temp']
            data_block['_exptl_crystal_size_max'] = self.cfg['max_crystal_dimension']
            data_block['_exptl_crystal_size_mid'] = self.cfg['middle_crystal_dimension']
            data_block['_exptl_crystal_size_min'] = self.cfg['min_crystal_dimension']
            data_block['_diffrn_radiation_monochromator'] = self.cfg[beamline +'_monochromator']
            data_block['_diffrn_radiation_source'] = self.cfg[beamline +'_source']
            data_block['_cell_measurement_reflns_used'] = self.C
            data_block['_cell_measurement_theta_min'] = self.A
            data_block['_cell_measurement_theta_max'] = self.B
            
            
            with open ('edited.cif', 'w') as updated:
                updated.write(cif.WriteOut())
                
            filenames.append(os.getcwd() + '/edited.cif')
            data_worked.append(counter)
            
        return filenames, data_worked
    
    def CIF_Combine(self, filenames, home_path):
        with open (home_path + '/results/' + 'all_cifs.cif', 'w') as combined_cif:
            for expt in filenames:
                with open(expt) as single_cif:
                    combined_cif.write(single_cif.read())
            
#A procedure to run SHELXT in the case where the structure may not be known (ie VT data with changing symmetry)
 
def solve_SHELXT():
    shelxt = subprocess.call(['shelxt', 'shelx'])
    os.remove('shelx.ins')
    os.rename('shelx_a.ins', 'shelx.ins')
    structure_INS.add_line('ACTA')
    structure_INS.add_line('WGHT      0.2000      0.1000')


#A function to refine using SHELXL and adjusting the weighting scheme each time

def refine_SHELXL():
    weight = []
    for m in range(0,10):
        shelxl = subprocess.call(['shelxl', 'shelx'])
        shutil.copy('shelx.res', 'shelx.ins')
        with open ('shelx.res', 'rt') as refinement:
            for line in refinement:
                if 'WGHT' in line:
                    weight.append(line)
        with open ('shelx.ins', 'rt') as initial:
            lines = initial.readlines()
        with open ('shelx.ins', 'w') as initial:
            for line in lines:
                if 'WGHT' in line:
                    initial.write(weight[1])
                else:
                    initial.write(line)

 





            
    

































    
    
    


#!/usr/bin/env python3


#This script is for VT analysis with two reference and one change in symmetry at an unknown point


#----------Required Modules----------#

import os 
import pandas as pd
import re
import yaml
from cif_analysis import Cell_Parameter, VT_Analysis_Cell_Parameter
from xprep import XPREP
from post_processing import INS_File, Reference_INS, New_INS, solve_SHELXT, refine_SHELXL, CIF_File
from file_setup import Setup

#----------Important Stuff----------#

def sorted_properly(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)

initialise = Setup()
cfg = initialise.cfg

initialise.Organise_Directory_Autoprocess()

#----------Post XDS----------#

counter = 0
filenames = []
data_worked = []

os.chdir('analysis')

#This part of the code pulls all of the temperature parameters from the autoprocess.cif 

if not os.path.exists(initialise.home_path + '/results/Just Temps.csv'):

    for run in sorted_properly(os.listdir()):
        try:
            os.chdir(run)
        except NotADirectoryError:
            pass
        else:
            for files in os.listdir():
                if 'autoprocess' in files:
                    with open (files, 'r') as cif_file:
                        lines = cif_file.readlines()
                    with open (initialise.home_path + '/results/temp_cif.cif', 'a') as combined:
                        for line in lines:
                            combined.write(line)
                            
                elif 'edited.cif' in files:
                    os.remove(files)
                elif 'shelx.cif' in files:
                    os.remove(files)
                    
                    
            os.chdir('..')
        
    os.chdir(initialise.home_path + '/results')    

    temp_params = Cell_Parameter(initialise.home_path)
    temp_df = temp_params.data()

    temp_df.to_csv('Just Temps.csv', index = None)

    os.remove('temp_cif.cif')

    os.chdir(initialise.home_path)

    os.chdir('analysis')
    
else:
    temp_df = pd.read_csv(initialise.home_path + '/results/Just Temps.csv')

for run in sorted_properly(os.listdir()):
    if os.path.isdir(run):
        counter += 1
        os.chdir(run)
        unit_cell = XPREP(initialise.home_path)
        unit_cell.run_XPREP_auto()
        try: 
            os.remove('shelx.pcf')
        except FileNotFOundError as error:
            unit_cell.logger.info('Failed to find a cell from the diffraction data - structure ' + str(counter))
            os.chdir('..')
            continue
        else:
            unit_cell.logger.info('Successfully identified a unit cell - structure ' + str(counter))
        
        structure_INS = New_INS('shelx.ins', initialise.home_path)
        
        file_size = os.stat(structure_INS.path) 
            
        if file_size.st_size < 10:
            structure_INS.logger.info('Error - INS file blank and XPREP failed - structure ' + str(counter))
            os.chdir('..')
            continue
        else:
            structure_INS.logger.info('Successfully created .ins file - structure ' + str(counter))
                
        new_SG = structure_INS.space_group
        
        solve_SHELXT() 
            
        refine_SHELXL()
                
        file_size = os.stat(structure_INS.path)
            
        if file_size.st_size < 10:
            structure_INS.logger.info('Refinement failed - structure ' + str(counter))
            os.chdir('..')
            continue
            
        current_CIF_File = CIF_File('shelx.cif', initialise.home_path)
            
        current_CIF_File.Datablock_Naming(counter)
            
        filenames, data_worked = current_CIF_File.Finalisation_Parameters(counter, filenames, data_worked)
            
        os.chdir('..')

current_CIF_File.CIF_Combine(filenames, initialise.home_path)

#This part deletes unnecessary files incase the script needs to be run multiple times 

for run in sorted_properly(os.listdir()):
    if os.path.isdir(run):
        os.chdir(run)
        try:
            os.remove('edited.cif')
        except FileNotFoundError:
            pass
        else:
            os.remove('shelx.cif')
        os.chdir('..')
        
#----------Analysis----------#

os.chdir(initialise.home_path + '/results/')
       
full_cell_data = VT_Analysis_Cell_Parameter(initialise.home_path)
cell_df = full_cell_data.data()

second_temp_df = pd.DataFrame(columns=['_diffrn_ambient_temperature'], index=data_worked)

for item in data_worked:
    second_temp_df.loc[item] = temp_df.loc[item-1] 
    
del cell_df['_diffrn_ambient_temperature']

cell_df['_diffrn_ambient_temperature'] = second_temp_df['_diffrn_ambient_temperature'].values

full_cell_data.process(cell_df)

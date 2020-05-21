# Welcome to CX-ASAP
A set of tools for analysing and collecting better CX data

## Overview
This software package is designed to improve throughput when processing large crystallographic datasets. If you have collections where you are examining subtle changes in a crystal structure and are measuring the same crystal under various conditions, here's how CX-ASAP can help! 

CX-ASAP consists of a range of different *modules* which can be tied together with a *pipeline*. Currently, pipelines need to be written by hand, although future development plans include making a GUI to do this for you! 

Types of experiments which can be automatically processed:
 * Variable Temperature
 * Flexible Mapping (contact amy.thompson2@uqconnect.edu.au for scripts)
 
This code works by using reference structures to refine against a range of collections so you don't need to solve the same structure 50 times! 

Note that in the case of a phase change, multiple reference structures are required (code in development)

Each of the modules can also be run independently! So feel free to only use bits and pieces as necessary for your data! 

## The config.yaml file... 

While a GUI is in development, users are currently required to enter parameters directly into the config.yaml file. While the file is not difficult to edit, there are a multitude of other parameters that are used by the code *only* and do complicate the process. So before using any modules, read the below documentation to see which fields you need to edit, and where the script should be run

## Python3 Libraries Required

* os
* shutil
* yaml
* logbook
* pathlib
* fileinput
* re
* pandas
* math
* subprocess
* CifFile (also called PyCifRW-4.4.1)
* matplotlib

## Variable Temperature Pipeline

This is the overall pipeline to analyse variable temperature data. This pipeline, ```variable_temperature_single_ref_pipeline.py```, is dependent on output from the Australian Synchrotron's Autoprocessing pipeline https://github.com/AustralianSynchrotron/mx-auto-dataset. 
It also requires a reference .ins file. Note that this should NOT be present in one of the structure folders you are processing through this software (please save in external location). 
Execute this pipeline in a directory where all of the autoprocessed folders are stored. 

**```conf.yaml``` parameters to edit --- from all of the individual modules:**

* file_name - Name of files common to all tests (ie if test_001, test_002, then this parameter should be set to 'test')
* experiment_type - This is used to name the main folder, examples include 'flexible_mapping' or 'variable_temperature'
* reference_path - Path to the reference '.ins' file including the file name (this should not be in any of the main data files you are analysing)
* second_reference_path - Path to the second reference file - keep this field blank if you only have one reference file 
* xprep_file_name - Name of the xprep files (should be consistent for all experiments), ie XDS_ASCII.HKL or XDS_ASCII.HKL_p1
* chemical_formula - Chemical formula of the crystal 
* beamline - beamline used, 'MX1' or 'MX2' (if left as blank, then the instrumentation parameters will not be added)
* crystal_colour - Colour of the crystal
* crystal_habit - Habit of the crystal
* temp - Temperature of experiment
* max_crystal_dimension - Largest crystal dimension (in mm)
* middle_crystal_dimension - Middle crystal dimension (in mm)
* min_crystal_dimension - Smallest crystal dimension (in mm)
* cell_parameters - A list of the parameters that are extracted from the CIF. The default will be fine fine for most experiments, only change if necessary (you must enter the terms exactly as they appear in the CIF)
* use_cif_headings - Are the headings of your data the same as the CIF parameters? If run as a full pipeline, they are and enter 'yes', if you are using external data with different headings, then enter 'no'
* user_headings_x - If you are using your own headings, type the name of the column which has your temperature data in it
* user_headings_y - If you are using your own headings, type the name of all columns which have your cell data in it 
* data_file_name - If you are using your own data, you will need to change this to the name of your '.csv' file. If you are using the full pipeline, use the default 'CIF_Parameters.csv' 

**Modules used:**

* ```file_setup_autoprocess.py```
* ```additional_setup_vt.py```
* ```xprep_ref.py```
* ```SHELXL_ref.py```
* ```cif_compile.py```
* ```cif_reading.py```
* ```variable_temp_analysis.py```

## Flexible Mapping Pipeline
Utilizes data obtained from microfocus beamlines such as the Australian Synchrotron MX2 beamline. Please contact Amy Thompson (amy.thompson2@uqconnect.edu.au) for further information.

# Authors
- **Amy Thompson**
- **Dr Kate Smith**
- **Dr Daniel Eriksson**
- **Dr Jason Price**

# Acknowledgements
- **Dr Arnaud Grosjean**

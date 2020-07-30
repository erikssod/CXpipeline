# Welcome to CX-ASAP! Please read the below guide to get started

## Introduction

This software package is designed to improve throughput when processing large crystallographic datasets. If you have collections where you are examining subtle changes in a crystal structure and are measuring the same crystal under various conditions, here's how CX-ASAP can help! 

CX-ASAP consists of a range of different *modules* which can be tied together with a *pipeline*. Currently, pipelines need to be written by hand, although future development plans include making a GUI to do this for you! 

Types of experiments which can be automatically processed:
 * Variable Temperature 
 * Flexible Mapping (contact amy.thompson2@uqconnect.edu.au for scripts)
 
This code works by using reference structures to refine against a range of collections so you don't need to solve the same structure 50 times! 

Note that in the case of a phase change, multiple reference structures are required. Currently, this means splitting your dataset at the phase transition, and running the code individually. Code is in development to process phase-change VT studies automatically.

Each of the modules can also be run independently! So feel free to only use bits and pieces as necessary for your data!

## Installation...

As this software is still in the early stages of development, there does not yet exist a simple 'installation' option. If you would like to use this code, please use the installation instructions document provided on GitHub. Unfortunately it may be a lengthy process, but the time you save processing data will be worth it! 

## The config.yaml file... 

While a GUI is in development, users are currently required to enter parameters directly into the config.yaml file. While the file is not difficult to edit, there are a multitude of other parameters that are used by the code *only* and do complicate the process. Only edit parameters under the heading 'User_Parameters_Full_Pipeline' or 'Extra_User_Parameters_Individual_Modules' if you are using individual modules of code. Note that using the individual modules is more likely to cause errors in these early stages of software development, and it is recommended that you run the full pipeline. 

## Python Libraries Required

* os
* shutil
* yaml (at least version 5.3.1)
* logbook
* pathlib
* fileinput
* re
* pandas
* math
* subprocess
* CifFile (also called PyCifRW)
* matplotlib
* statistics
* numpy

### pipelines/variable_temperature_single_ref_pipeline

This is the overall pipeline to analyse variable temperature data. This pipeline is dependent on the Australian Synchrotron's Autoprocessing pipeline running prior. It also requires a reference .ins file. Note that this should NOT be present in one of the structure folders you are processing through this software (please save in external location). Execute this pipeline in a directory where all of the autoprocessed folders are stored. IF any have failed the autoprocessing, it is recommended that you process it manually in XDS prior to running the script, otherwise these datasets will be removed from the analysis. 

**conf.yaml parameters to edit:**
    
* atoms_for_rotation - Provide a list of atoms that you would like the mean planes analysis for comparison with a reference. This may provide insight as to how the molecule is moving within the unit cell. Make sure you use the same atom names as used in your reference structure  
* reference_plane - This is the plane your atoms will be compared against. Make sure you notate it in miller indices such as '100' 
* cell_parameters - This is the list of parameters to extract from your CIF files for analysis. The default list should be fine in most cases and will hardly need changing. Note that if you do change, you will be required to enter the parameters as notated in the CIF file (for instance '_cell_length_a' instead of 'a-axis')
* beamline - Enter MX1 or MX2 depending on which beamline your experiment was done on. This will be used for CIF editing 
* wavelength - Enter the wavelength of x-rays used
* chemical_formula - Enter the chemical formula of your crystal 
* crystal_colour - Enter the colour of your crystal
* crystal_habit - Enter the habit of your crystal
* max_crystal_dimension - Enter the largest dimension of your crystal (in mm)
* middle_crystal_dimension - Enter the middle dimension of your crystal (in mm)
* min_crystal_dimension - Enter the smallest dimension of your crystal (in mm)
* file_name - Enter the common file name between temperatures in your VT collection 
* reference_path - Enter the path to your reference .ins file (including the file name!)
* second_reference_path - Since this is a single reference pipeline, you should make sure this field is blank (or just enter '')
* xprep_file_name - Enter which xprep file you wish to start from (ie XDS_ASCII.HKL_p1) 
* refinements_to_check - How many of the least squares iterations will be checked (from the most recent backwards)
* tolerance - The target average shift of the refinements that are being analysed 

**Modules used:**

* file_setup_autoprocess.py
* additional_setup_vt.py
* xprep_ref.py
* SHELXL_ref.py
* rotation_planes_vt.py
* cif_compile.py
* cif_reading.py
* variable_temp_analysis.py

### modules/file_setup_autoprocess.py

This module prepares the directory tree and sets up the config.yaml file for data based on the synchrotron's autoprocessing pipeline. It should be run in the same directory as all of the autoprocessed folders 

**conf.yaml parameters for user to edit:**

* file_name - Enter the common file name between temperatures in your VT collection 
* reference_path - Enter the path to your reference .ins file (including the file name!)
* second_reference_path - Since this is a single reference pipeline, you should make sure this field is blank (or just enter '')

### modules/additional_setup_vt.py

This module performs additional setup for variable temperature experiments, and should be run from the same location as file_setup_autoprocess.py. Should be run in conjunction with file_setup_autoprocess.py. 

**conf.yaml parameters for user to edit:**

None

### modules/xprep_ref.py

This module runs xprep for all datsets in folders based on reference space group from '.ins' file. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* xprep_file_name - Enter which xprep file you wish to start from (ie XDS_ASCII.HKL_p1)
* chemical_formula - Enter the chemical formula of your crystal

### modules/SHELXL_ref.py

This module runs SHELXL for all datasets in folders based on reference structure from '.ins' file which is imported prior to refinement. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* ref_ins_path - Enter the path to your reference .ins file (including the file name!)
* refinements_to_check - How many of the least squares iterations will be checked (from the most recent backwards)
* tolerance - The target average shift of the refinements that are being analysed 

### modules/rotation_planes_vt.py

This module analyses the '.lst' file for all datasets in folders and calculates the angle with respect to a defined reference plane. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* reference_plane - This is the plane your atoms will be compared against. Make sure you notate it in miller indices such as '100' 
* temperature_path - path to the .csv file containing the temperatures used in the VT experiment
* temperature_heading - heading used at the top of the temperature column in the .csv file

### modules/cif_compile.py

This module combines all of the CIF files present in the folders and renames them numerically. It also adds instrumentation parameters for finalisation. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* chemical_formula - Chemical formula of the crystal
* beamline - beamline used, 'MX1' or 'MX2' 
* crystal_colour - Colour of the crystal
* crystal_habit - Habit of the crystal
* max_crystal_dimension - Largest crystal dimension (in mm)
* middle_crystal_dimension - Middle crystal dimension (in mm)
* min_crystal_dimension - Smallest crystal dimension (in mm)
* temperature_path - path to the .csv file containing the temperatures used in the VT experiment
* temperature_heading - heading used at the top of the temperature column in the .csv file

### modules/cif_reading.py

This module reads all of the CIF files present in a folder and below in the directory tree and extracts the desired parameters and saves it to a '.csv' file. This module should be executed from the highest folder containing all the necessary CIF files. 

**conf.yaml parameters for user to edit:**

* cell_parameters - This is the list of parameters to extract from your CIF files for analysis. The default list should be fine in most cases and will hardly need changing. Note that if you do change, you will be required to enter the parameters as notated in the CIF file (for instance '_cell_length_a' instead of 'a-axis')

### modules/variable_temp_analysis.py

This module performs a basic analysis for a variable temperature experiment - all of the cell parameters are plotted against temperature. This module should be executed from the folder containing the '.csv' file of all cell parameters. 

**conf.yaml parameters for user to edit:**

* cell_parameters - A list of the parameters that are extracted from the CIF. The default will be fine fine for most experiments, only change if necessary (you must enter the terms exactly as they appear in the CIF)
* use_custom_headings - Are the headings of your data different to the CIF parameters? If run as a full pipeline, they are and enter 'no', if you are using external data with different headings, then enter 'yes'
* user_headings_x - If you are using your own headings, type the name of the column which has your temperature data in it
* user_headings_y - If you are using your own headings, type the name of all columns which have your cell data in it 
* data_file_name - Enter the name of your .csv file containing all cell parameters and the temperatures of the VT experiment

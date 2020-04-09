# Welcome to CX-ASAP! Please read the below guide to get started

## Introduction

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

## Python Libraries Required

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

### pipelines/variable_temperature_single_ref_pipeline

This is the overall pipeline to analyse variable temperature data. This pipeline is dependent on the Australian Synchrotron's Autoprocessing pipeline running prior. It also requires a reference .ins file. Note that this should NOT be present in one of the structure folders you are processing through this software (please save in external location). Execute this pipeline in a directory where all of the autoprocessed folders are stored. 

**conf.yaml parameters to edit --- from all of the individual modules:**

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

* file_setup_autoprocess.py
* additional_setup_vt.py
* xprep_ref.py
* SHELXL_ref.py
* cif_compile.py
* cif_reading.py
* variable_temp_analysis.py

### modules/file_setup_autoprocess.py

This module prepares the directory tree and sets up the config.yaml file for data based on the synchrotron's autoprocessing pipeline. It should be run in the same directory as all of the autoprocessed folders 

**conf.yaml parameters for user to edit:**

* file_name - Name of files common to all tests (ie if test_001, test_002, then this parameter should be set to 'test')
* experiment_type - This is used to name the main folder, examples include 'flexible_mapping' or 'variable_temperature'
* reference_path - Path to the reference '.ins' file including the file name (this should not be in any of the main data files you are analysing)
* second_reference_path - Path to the second reference file - keep this field blank if you only have one reference file 

**conf.yaml parameters used by the system only:**

* home_path - The path to the folder where the analysis starts from - also used to define the path to the error log file
* analysis_path - The path to the analysis folder
* ref_path - The path to the reference folder 
* results_path - The path to the results folder
* failed_path - The path to the folder of data that failed autoprocessing
* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate
* ref_ins_path - The path to the reference file within the home path after it has been copied 

### modules/file_setup_reprocessing.py

This module prepares the directory tree and sets up the config.yaml file for reprocessing raw frames through XDS. It should be run in the same directory as all of the required frames. 

**conf.yaml parameters for user to edit:**

* file_name - Name of files common to all tests (ie if test_001, test_002, then this parameter should be set to 'test')
* experiment_type - This is used to name the main folder, examples include 'flexible_mapping' or 'variable_temperature'
* reference_path - Path to the reference '.ins' file including the file name (this should not be in any of the main data files you are analysing)
* xds_reference_path - Path to the reference 'XDS.INP' file including the file name

**conf.yaml parameters used by the system only:**

* home_path - The path to the folder where the analysis starts from - also used to define the path to the error log file
* analysis_path - The path to the analysis folder
* ref_path - The path to the reference folder 
* results_path - The path to the results folder
* frames_path - The path to the folder of data that failed autoprocessing
* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate
* XDS_INP_path - The path to the reference 'XDS.INP' file within the home path after it has been copied 
* ref_ins_path - The path to the reference file within the home path after it has been copied 

### modules/additional_setup_vt.py

This module performs additional setup for variable temperature experiments, and should be run from the same location as file_setup_autoprocess.py. 

**conf.yaml parameters for user to edit:**

None

**conf.yaml parameters used by the system only:**

* results_path - The path to the results folder
* analysis_path - The path to the analysis folder
* ref_ins_path - The path to the reference file within the home path after it has been copied
* space_group - The space group from the reference '.ins' file written using the following notation P2(1)/n
* ref_INS_a - The a-axis from the reference '.ins' file
* ref_INS_b - The b-axis from the reference '.ins' file
* ref_INS_c - The c-axis from the reference '.ins' file
* ref_INS_alpha - The alpha angle from the reference '.ins' file
* ref_INS_beta - The beta angle from the reference '.ins' file
* ref_INS_gamma - The gamma angle from the reference '.ins' file
* ref_INS_volume - The volume calculated based on the cell in the reference '.ins' file 
* temps_already_in_cifs - As the full pipeline is being used, this parameter sets up the temperatures to be found from the autoprocess.cif files 

### modules/xds.py

This module runs XDS for all datasets in folders based on the reference 'XDS.INP' file. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

None 

**conf.yaml parameters used by the system only:**

* analysis_path - The path to the analysis folder
* XDS_INP_path - The path to the reference 'XDS.INP' file within the home path after it has been copied 

### modules/xprep_ref.py

This module runs xprep for all datsets in folders based on reference space group from '.ins' file. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* xprep_file_name - Name of the xprep files (should be consistent for all experiments), ie XDS_ASCII.HKL or XDS_ASCII.HKL_p1
* chemical_formula - Chemical formula of the crystal 

**conf.yaml parameters used by the system only:**

* analysis_path - The path to the analysis folder
* space_group - The space group from the reference '.ins' file written using the following notation P2(1)/n

### modules/SHELXL_ref.py

This module runs SHELXL for all datasets in folders based on reference structure from '.ins' file which is imported prior to refinement. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* ref_ins_path - The path to the reference file within the home path after it has been copied

**conf.yaml parameters used by the system only:**

* analysis_path - The path to the analysis folder

### modules/rotation_planes.py

This module analyses the '.lst' file for all datasets in folders and calculates the angle with respect to a defined reference plane. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* reference_plane - Define the plane to be used as the reference - example notation: '[100]', '[010]'
* mapping_step_size - Define the step size (in micro-metres) between measurements 

**conf.yaml parameters used by the system only:**

* analysis_path - The path to the analysis folder
* process_counter - This counds how many times XDS is run (in the case of testing multiple parameters)
* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate

### modules/cif_compile.py

This module combines all of the CIF files present in the folders and renames them numerically. It also adds instrumentation parameters for finalisation. It should be executed in the folder which contains the folders of all data sets. 

**conf.yaml parameters for user to edit:**

* chemical_formula - Chemical formula of the crystal
* beamline - beamline used, 'MX1' or 'MX2' (if left as blank, then the instrumentation parameters will not be added)
* crystal_colour - Colour of the crystal
* crystal_habit - Habit of the crystal
* temp - Temperature of experiment
* max_crystal_dimension - Largest crystal dimension (in mm)
* middle_crystal_dimension - Middle crystal dimension (in mm)
* min_crystal_dimension - Smallest crystal dimension (in mm)

**conf.yaml parameters used by the system only:**

* analysis_path - The path to the analysis folder
* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate
* data_collection - Method of data collection
* absorp_correction - Method of absorption correction
* wavelength - Radiation wavelength
* radiation_type - Type of radiation
* detector - Detector used
* measurement_method - Type of scan (ie Omega)
* cell_refinement - Program used for cell refinement
* structure_soln - Program used for structure solution
* monochromator - monochromator used 
* source - Radiation source 

### modules/cif_reading.py

This module reads all of the CIF files present in a folder and below in the directory tree and extracts the desired parameters and saves it to a '.csv' file. This module should be executed from the highest folder containing all the necessary CIF files. 

**conf.yaml parameters for user to edit:**

* cell_parameters - A list of the parameters that are extracted from the CIF. The default will be fine for most experiments, only change if necessary (you must enter the terms exactly as they appear in the CIF)

**conf.yaml parameters used by the system only:**

* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate
* Structures_in_each_CIF - This counts the number of structures per cif and saves to a list - this parameter is reset every time this module is run 
* Successful_Positions - This notes which positions were actually successful (ie out of 40 structures, 12-30 were successful) - this parameter is reset every time this module is run 

### modules/variable_temp_analysis.py

This module performs a basic analysis for a variable temperature experiment - all of the cell parameters are plotted against temperature. This module should be executed from the folder containing the '.csv' file of all cell parameters. 

**conf.yaml parameters for user to edit:**

* cell_parameters - A list of the parameters that are extracted from the CIF. The default will be fine fine for most experiments, only change if necessary (you must enter the terms exactly as they appear in the CIF)
* use_cif_headings - Are the headings of your data the same as the CIF parameters? If run as a full pipeline, they are and enter 'yes', if you are using external data with different headings, then enter 'no'
* user_headings_x - If you are using your own headings, type the name of the column which has your temperature data in it
* user_headings_y - If you are using your own headings, type the name of all columns which have your cell data in it 
* data_file_name - If you are using your own data, you will need to change this to the name of your '.csv' file. If you are using the full pipeline, use the default 'CIF_Parameters.csv' 
* temps_already_in_cifs - If your temperature values are already in the cif files, set this parameter to 'yes', otherwise, set as 'no' (if being used as a part of the pipeline, the system will automatically set this to 'no')

**conf.yaml parameters used by the system only:**

* current_results_path - The path to the current results folder, as it makes a new mini-folder each time the code is run to keep results separate
* results_path - The path to the overall results folder (where the temperature data is kept) 



































































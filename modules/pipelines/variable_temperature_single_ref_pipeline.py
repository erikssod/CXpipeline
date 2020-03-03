#!/usr/bin/env python3

####################################################################################
#-------------CX-ASAP: variable_temperature_single_reference_pipeline--------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#This module acts as the overall pipeline for flexible crystal analysis 

#----------Required Modules----------#

from modules.file_setup_autoprocess import Setup
from modules.additional_setup_vt import VT_Setup
from modules.xprep_ref import XPREP
from modules.SHELXL_ref import SHELXL
from modules.cif_compile import CIF_Combine
from modules.cif_reading import CIF_File
from modules.variable_temp_analysis import VT_Analysis

#----------Pipeline----------#
initialisation = Setup()
initialisation.Organise_Directory_Tree()
more_setup = VT_Setup()
more_setup.Temperature_Collection()
more_setup.Ref_Setup()
cell_analysis = XPREP(home_path = initialisation.cfg['home_path'])
cell_analysis.run_xprep()
refinement = SHELXL(home_path = initialisation.cfg['home_path'])
refinement.run_shelxl()
combine = CIF_Combine(home_path = initialisation.cfg['home_path'])
combine.combine()
analysis = CIF_File(home_path = initialisation.cfg['home_path'])
data = analysis.get_data()
analysis.data_output()
vt_analysis = VT_Analysis(home_path = initialisation.cfg['home_path'])
vt_analysis.import_data(vt_analysis.cfg['data_file_name'])
vt_analysis.analysis()


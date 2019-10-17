Data Analysis modules go here

Xprep Graphs for a single dataset (Kate)

Unit Cell Analysis (Amy)

Amy:
vt_analysis_no_symmetry_change.py allows for full analysis using the synchrotron's automatic processing 

Am also working on a version of this script for systems with unknown symmetry (might have phase changes), as well as a version where two references can be used if the system is known to go through two different symmetries

A script for flexible analysis is still in the works :) 

file_setup.py - organises files so that the script can be run straight from the output from the synchrotron 

xprep.py - as the name suggests, options for forcing spacegroup or accepting what xprep thinks 

post_processing.py - SHELXT/SHELXL/CIF finalisation occurs here

cif_analysis.py - pulls wanted parameters from cif files and analyses depending on the type of experiment

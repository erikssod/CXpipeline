Data Analysis modules go here

Xprep Graphs for a single dataset (Kate)

Unit Cell Analysis (Amy)

Amy:
vt_analysis_no_symmetry_change.py allows for full analysis using the synchrotron's automatic processing 

vt_analysis_unknown_changes.py does not assume any symmetry and goes through xprep/shelxt/shelxl automatically with cell analysis/output - should always be checked and not heavily relied on, but might provide a useful indication as to how the system is behaving for preliminary feedback 

Am also working on a version where two references can be used if the system is known to go through two different symmetries

A script for flexible analysis is still in the works :) 

file_setup.py - organises files so that the script can be run straight from the output from the synchrotron 

xprep.py - as the name suggests, options for forcing spacegroup or accepting what xprep thinks 

post_processing.py - SHELXT/SHELXL/CIF finalisation occurs here

cif_analysis.py - pulls wanted parameters from cif files and analyses depending on the type of experiment

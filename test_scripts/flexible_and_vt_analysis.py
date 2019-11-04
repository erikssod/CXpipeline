#!/usr/bin/env python3


#----------Things to Add for Future Versions----------#
#   - Error calculations/bars for graphs - already have the errors in the cell dimensions, but would need to calculate for the percent deformations 
#   - Get the Space Group from reference somewhere - have the space group, but also need the number (perhaps a dictionary to convert and does this already exist?)
#   - Get the chemical formula from reference
#   - Way to omit dodgy frames
#   - Shading? Sometimes a problem with blu-tac mounting for bendy crystals
#   - change name of ref (ask if 'xxx.ins' is reference? if so, make this the ref_path)
#   - FOR VT DATA COULD MAYBE IMPORT MULTIPLE REFERENCES - SO IF THERE IS A SPACE GROUP CHANGE COULD STILL COPY/PASTE REFERENCE STRUCTURES AND GET TO FINALISED CIFS


#----------Things to Figure out at Synchrotron----------#
#   - Automate pulling all the correct files into one folder OR integrate with current autoprocess and do it on the fly as collecting 
#   - Where to get temperature values for VT collections (for data analysis / graphical output)
#   - Make sure their automated filenames work with this code 
#   - Absorption corrections? Important for VT - how to integrate SADABS
#   - CIF Editing - check parameters for MX1 vs MX2 


#----------Current Level of User Input----------#
#   - Place the following files in a single folder:
#       - all frames
#       - finalised reference structure (ref.ins) - not strictly required, but for finalised structures need this - mainly applicable to flexible mapping OR VT studies without symmetry changes
#       - GXPARM.XDS (instrument parameters from REFERENCE), BKGINIT.cbf, BLANK.cbf, GAIN.cbf, X-CORRECTIONS.cbf, Y-CORRECTIONS.cbf (background from REFERENCE) - - - These are only required for flexible mapping analysis
#       - XDS.INP (if flexible mapping, this should be from a MAPPING run NOT THE REFERENCE - so that it can read the starting angle/total data range)
#   - Edit variables for chemical formula and space group
#   - Enter correct location of dectris-neggia libraries AND maximum number of processors for XDS to use in the XDS input file class Definitions
#   - Answer questions as prompted by the commandline (things like crystal dimensions/description, whether it is flexible or VT, step-size for mapping, what type of analysis to do (mapping)


#----------Current Output----------#
#   - Finalised CIF files (if reference structure provided and NO changes to crystal symmetry)
#   - Error report so can see which structures worked and which didn't
#   - Extracted cell parameters and information about the experiment into a .csv file
#   - For flexible mapping: graphs of the Rint and Completeness, graphs of unit cell deformation
#   - For VT: graphs of how each cell parameter changes with temperature 

  
#----------Helpful Addition When Testing Blocks of Code----------#
#while True:
    #try:
        #test = int(input('Enter 1 to continue: '))
    #except ValueError:
        #print('Error! Invalid entry')
    #else:
        #if test == 1:
            #break  


#----------Synchrotron Beamline Details----------# THIS WILL PROBABLY NEED CORRECTION - remove ones which are the same once confirm (also edit absorption correction for vt depending how gets integrated)
# MX1:

MX1_data_collection = 'AS QEGUI'
MX1_absorp_correction = 'none'
MX1_radiation_type = 'synchrotron'
MX1_measurement_method = 'Omega Scan'
MX1_cell_refinement = 'XDS (Kabsch, 1993)'
MX1_structure_soln = 'known structure'
MX1_monochromator = 'Silicon Double Crystal'
MX1_source = 'MX1 Beamline Australian Synchrotron'
MX1_detector = 'Dectris Eiger X 8M'

# MX2:

MX2_data_collection = 'AS QEGUI'
MX2_absorp_correction = 'none'
MX2_radiation_type = 'synchrotron'
MX2_measurement_method = 'Omega Scan'
MX2_cell_refinement = 'XDS (Kabsch, 1993)'
MX2_structure_soln = 'known structure'
MX2_monochromator = 'Silicon Double Crystal'
MX2_source = 'MX2 Beamline Australian Synchrotron'
MX2_detector = 'Dectris Eiger X 16M'

       
#----------Required Modules----------#


import os 
import shutil
import subprocess
import pandas as pd
import math
import fileinput
import re
from CifFile import ReadCif
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 


#----------Class Definitions----------#


class Cell_Parameter:  
    
    
    #The Cell_Parameter class is used to pull cell parameters from CIF files based on an input search term, and output them (with separated errors) into lists


    def __init__(self, name):
        self.results = []
        self.search_name = name
        self.cif_files = []
        self.errors = []
        self.number_of_structures_in_cif = []
    
    #This function is required because with the current numbering system, it orders as 1, 10, 2, 3 etc instead of 1, 2, 3, 10
    
    def sorted_properly(self, data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    #This function goes through every CIF file in the current directory and below in the correct sorted order to extract the cell parameters 
    
    def data(self):
        for dirName, subdirList, fileList in os.walk(os.getcwd()):
            
            #Sorts into correct order 
            
            sorted_fileList = self.sorted_properly(fileList)
            for file in sorted_fileList:
                
                #Makes sure that the same file is not used multiple times (left over from analysing VT data from the home-source diffy which had copies of cif files in multiple folders)
                
                if file.endswith('.cif') and file.lower() not in self.cif_files:
                    self.cif_files.append(file.lower())
                    with open(os.path.join(dirName, file), 'rt') as cif:
                        temp4 = 0
                        for line in cif:
                            if self.search_name in line:
                                temp4 += 1
                                
                                #This handles the different cases of 1) An error present that has decimal places, 2) An error present which is exactly as written,3 )cases where there is no error present (ie angles of 90 and sometimes volume)
                                
                                if '(' in line:
                                    temp = line.strip(self.search_name).strip(' \n').split('(')
                                    temp3 = temp[1].strip(')')
                                    self.results.append(float(temp[0]))
                                    if '.' in line:
                                        temp2 = temp[0].split('.')
                                        self.errors.append(int(temp3)*10**-(int(len(temp2[1]))))
                                    else:
                                        self.errors.append(int(temp3))
                                else:
                                    temp = line.strip(self.search_name).strip(' \n')
                                    self.results.append(float(temp))
                                    self.errors.append(0)
                        self.number_of_structures_in_cif.append(temp4)            
        return self.results, self.errors, self.number_of_structures_in_cif, self.cif_files

    def __repr__(self):
        return "Parameter {} contains a list of values and errors from all CIF files in working directory".format(self.search_name) 


class XDS_Input_File:
        
    #The XDS_Input_File class sets up the XDS.INP file for easy editing, and provides an easy way TO edit them and retrieve values

    def __init__(self, path="XDS.INP"):
        self.path = path
        self.angle = 0
        self.value = ''
        self.total = 0
        
        #The below values will require changing for different systems 
        
        self.change("MAXIMUM_NUMBER_OF_PROCESSORS", 10)
        self.change("LIB", "/usr/local/bin/XDS_Tools/dectris-neggia.so")
        
        #To make editing the file easier later, the file is rewritten upon initialisation to put each keyword on a new line 
        
        with open(self.path, 'r+') as in_file:
            lines = in_file.readlines()
        with open('temp.INP', 'w') as out_file:
            for line in lines:
                
                #Multiple '=' signs indicate more than one keyword, EXCEPT for the headers used by XDS 
                
                if line.count('=') > 1 and '!' not in line:
                    index_current = 0
                    index_old = 0
                    new_line = ''
                    for character in line:
                        
                        #Splits the line at the spaces between different keywords/parameters (elif statement to make sure the last keyword isn't deleted due to a space NOT being present at the end of the line)
                        
                        if character == ' ' and line[index_current-1] != ' ' and line[index_current+1] == ' ':
                            new_line += ' ' + line[index_old:index_current+1].strip() + '\n'
                            index_old = index_current
                        elif line.endswith(character) and len(new_line) != 0:
                            new_line += ' ' + line[index_old:index_current+1].strip() + '\n'
                        index_current += 1    
                    out_file.write(new_line)        
                else:
                    out_file.write(line)
        shutil.move('temp.INP', self.path)
                            
    #Function to edit values 
    
    def change(self, parameter, new_value):
        flag = 0
        editing = '' 
        with open (self.path, 'rt') as in_file:
            for line in in_file:
                if parameter in line and flag == 0:
                    to_edit = line.split()[1:]
                    flag += 1
        for element in to_edit:
            editing += ' ' + str(element)
        edit = editing.strip(' ')
        flag = 0
        for line in fileinput.input(self.path, inplace = True):
            if parameter in line and flag == 0:
                line = line.rstrip('\r\n')    
                print(line.replace(edit, str(new_value)))
                flag += 1
            else:
                line = line.rstrip('\r\n')
                print(line)
            
    #Gets start and total angle - required later during editing to 'remember' what originally was 
    
    def start_angle(self):
        with open (self.path, 'rt') as in_file:
            for line in in_file:
                if "STARTING_ANGLE= " in line:
                    self.angle = float(line.split()[1])
                elif "DATA_RANGE= " in line:
                    frames = line.split()[2]
                    self.total = int(float(frames)) / 10
        return self.angle, self.total
    
    #Function to simply get the value of a keyword (general)
    
    def get_value(self, parameter):
        self.value = ''
        with open (self.path, 'rt') as in_file:
            for line in in_file:
                if parameter in line:
                    val_list = line.split()[1:]
        for element in val_list:
            self.value += '' + str(element)
        return self.value
                        
    def __repr__(self):
        return "XDS.INP File"    
    
class Variable_Temperature_XDS_Input_File(XDS_Input_File):
    
    #A subclass which puts changes the job to all jobs upon initialisation - this may not be needed once see how the synchrotrons systems actually work 
    
    def __init__(self, path = "XDS.INP"):
        super().__init__(path)
        self.change("JOB", "XYCORR INIT COLSPOT IDXREF DEFPIX INTEGRATE CORRECT")

class Flexible_Mapping_XDS_Input_File(XDS_Input_File):
    
    #A subclass which puts required keywords into the file for editing, and sets default values - don't want to refine beam or position, because not enough data and refining these introduces error (thus use instrument parameters from reference structure) 
    
    def __init__(self, path = "XDS.INP"):
        super().__init__(path)
        self.change("JOB", "COLSPOT IDXREF DEFPIX INTEGRATE CORRECT")
        self.change("NAME_TEMPLATE_OF_DATA_FRAMES", "img")
        self.change("SPOT_MAXIMUM-CENTROID", 2)
        self.change("MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT", 2)
        self.change("STRONG_PIXEL", 2)
        with open (self.path, 'rt') as in_file:
            flag1 = 0
            flag2 = 0
            flag3 = 0
            flag4 = 0
            flag5 = 0
            for line in in_file:
                if "MINIMUM_FRACTION_OF_INDEXED_SPOTS" in line:
                    self.change("MINIMUM_FRACTION_OF_INDEXED_SPOTS", 0.2)
                    flag1 += 1
                elif "SEPMIN" in line:
                    self.change("SEPMIN", 7)
                    flag2 += 1
                elif "REFINE(INTEGRATE)" in line:
                    self.change("REFINE(INTEGRATE)", "ORIENTATION CELL AXIS !BEAM POSITION") 
                    flag3 += 1
                elif "REFINE(IDXREF)" in line:
                    self.change("REFINE(IDXREF)", "ORIENTATION CELL AXIS !BEAM POSITION")
                    flag4 += 1
                elif "REFINE(CORRECT)" in line:
                    self.change("REFINE(CORRECT)", "ORIENTATION CELL AXIS !BEAM POSITION")
                    flag5 += 1
        with open (self.path, 'a') as in_file:
            if flag1 == 0:
                in_file.write(" MINIMUM_FRACTION_OF_INDEXED_SPOTS= 0.2\n")
            if flag2 == 0:
                in_file.write(" SEPMIN= 7\n")
            if flag3 == 0:
                in_file.write(" REFINE(INTEGRATE)= ORIENTATION CELL AXIS !BEAM POSITION\n")
            if flag4 == 0:
                in_file.write(" REFINE(IDXREF)= ORIENTATION CELL AXIS !BEAM POSITION\n")
            if flag5 == 0:
                in_file.write(" REFINE(CORRECT)= ORIENTATION CELL AXIS !BEAM POSITION\n")
                
class INS_File:
    
    #The INS_File class finds all cell parameters and saves them to a property of the object - also has the ability to add lines to the INS file

    def __init__(self, path_to_self):
        self.path = path_to_self
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
        
    #Function to add lines to the .ins file - places them after the plan line (because editing things like ACTA, weighting, etc, don't really want to mess around with the symmetry at the top)
    
    def add_line(self, parameter):
        with open (self.path, 'rt') as ins_file:
            lines = ins_file.readlines()
        with open (self.path, 'w') as ins_file:
            for line in lines:
                if 'PLAN' not in line:
                    ins_file.write(line)
                else:
                    ins_file.write(parameter + '\n')
                    ins_file.write(line)

    def __repr__(self):
        return "Crystallographic Instruction File"
    
class Reference_INS(INS_File):
    
    #A subclass which saves the structure part of the ins so that it can be 'pasted' into new ins files to refine against

    def __init__(self, path):
        super().__init__(path)
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

    def __init__(self, path):
        super().__init__(path)
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
        
        
#----------Function Definitions----------#


#This function is also set out here because also need it to order run files correctly 

def sorted_properly(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)

#A nice short function to run XDS - just made it for readability and organisation

def run_XDS():
    os.system('xds_par')
 
#A procedure to run XPREP based on a known space group and chemical formula
 
def run_XPREP_known():
    xprep = subprocess.Popen(['xprep'], stdin = subprocess.PIPE, encoding='utf8')
    xprep.stdin.write('XDS_ASCII.HKL\n')
    xprep.stdin.write('X\n')
    xprep.stdin.write('Y\n')
    xprep.stdin.write('P\n')
    xprep.stdin.write('U\n')
    xprep.stdin.write('O\n')
    xprep.stdin.write('1 0 0 0 1 0 0 0 1\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('I\n')
    xprep.stdin.write(SG + '\n')
    xprep.stdin.write('Y\n')
    xprep.stdin.write('D\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('A\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('E\n')
    xprep.stdin.write('C\n')
    xprep.stdin.write(formula + '\n')
    xprep.stdin.write('E\n')
    xprep.stdin.write('F\n')
    xprep.stdin.write('shelx\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('Y\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('Q\n')
    xprep.stdin.close()
    xprep.wait()
    
    
#A procedure to accept whatever xprep thinks - equivalent to a person sitting there and just pressing enter for everything    
  
def run_XPREP_auto():
    xprep = subprocess.Popen(['xprep'], stdin = subprocess.PIPE, encoding='utf8')
    xprep.stdin.write('XDS_ASCII.HKL\n')
    xprep.stdin.write('X\n')
    xprep.stdin.write('Y\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('H\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('D\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('A\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('E\n')
    xprep.stdin.write('C\n')
    xprep.stdin.write(formula + '\n')
    xprep.stdin.write('E\n')
    xprep.stdin.write('F\n')
    xprep.stdin.write('shelx\n')
    xprep.stdin.write('S\n')
    xprep.stdin.write('Y\n')
    xprep.stdin.write('\n')
    xprep.stdin.write('Q\n')
    xprep.stdin.close()
    xprep.wait()
    
    
#A procedure to run SHELXT in the case where the structure may not be known (ie VT data with changing symmetry)
#Adds in a line to adjust the weighting, and adds in an ACTA command to generate a CIF
#Chooses the first one that SHELXT suggests (shelx_a.ins)
 
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
 
 
#Questions asked to the user for the purpose of finalising CIF files
                    
def CIF_finalisation_questions():
    while True:
        try:
            habit = input('Please enter crystal habit: ')
        except:
            print ('Error!')
        else:
            letter_flag = 0
            for letter in habit:
                if letter.isdigit() == True:
                    letter_flag += 1
            if letter_flag == 0:
                break
            else:
                print('Please enter a string of letters only!')
                
    while True:
        try:
            colour = input('Please enter crystal colour: ')
        except:
            print ('Error!')
        else:
            letter_flag = 0
            for letter in colour:
                if letter.isdigit() == True:
                    letter_flag += 1
            if letter_flag == 0:
                break
            else:
                print('Please enter a string of letters only!')
                
    while True:
        try:
            max_size = float(input('Please enter maximum crystal dimension (in mm): '))
        except ValueError:
            print('Error!')
        else:
            if max_size > 0 and max_size < 40:
                break
            else:
                print('Are you sure your crystal is that big?')
            
    while True:
        try:
            mid_size = float(input('Please enter middle crystal dimension (in mm): '))
        except ValueError:
            print('Error!')
        else:
            if mid_size > 0 and mid_size <= max_size:
                break
            else:
                print('Error: middle size larger than maximum size')
            
    while True:
        try:
            min_size = float(input('Please enter minimum crystal dimension (in mm): '))
        except ValueError:
            print('Error!')
        else:
            if min_size > 0 and min_size <= mid_size:
                break
            else:
                print('Error: minimum size larger than middle size')
                
    return habit, colour, max_size, mid_size, min_size            
  
#This function is the main process - it goes through the folders of different experiments and runs XDS/XPREP/SHELX and compiles them all into one cif file
  
def process_data(process_counter):
    
    #Setting up counters and placeholders
    
    counter = 0
    filenames = []
    if no_ref_flag == 0:
        initial_SG = ref_INS.space_group
    
    #Loop through all folders and process data (need the sorted_properly function to make sure the order isn't silly which may mess up with data order later)
    
    for run in sorted_properly(os.listdir()):
        counter += 1
        
        #Copy file first so that the 'master' input file remains unchanged
        
        shutil.copyfile(XDS_INP, home_path + '/input/temp.INP')
        XDS_Input.change('NAME_TEMPLATE_OF_DATA_FRAMES', 'img/' + run + '_??????.h5')
        os.chdir(run)
        shutil.copy(XDS_INP, os.getcwd())
        os.remove(XDS_INP)
        os.rename(home_path + '/input/temp.INP', XDS_INP)
        run_XDS()
        
        #SADABS or other absorption correction here if needed
        
        #Flexible mapping has low data and thus needs known space group - VT has more data and can sometimes have phase changes, as such even if a reference structure is provided, the space group is not forced 
        
        if expt_type == 1:
            run_XPREP_known()
        else:
            run_XPREP_auto()
        
        #Arnaud's 'toxic file' removal - also indicator that xprep did/didn't work - write errors to report, leave expt folder and continue with next item in loop if failed 
        
        if 'shelx.pcf' not in os.listdir():
            XDS_XPREP_status = 'Failed to find a cell from the diffraction data - structure ' + str(counter) + '\n'
            SHELXL_status = 'Did not even get to refinement - structure ' + str(counter) + '\n'
            os.chdir('..')
            with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'a') as report:
                report.write(XDS_XPREP_status)
                report.write(SHELXL_status)
            continue
        else:
            XDS_XPREP_status = 'Successfully identified a unit cell - structure ' + str(counter) + '\n'

        os.remove('shelx.pcf')
        
       #Makes a back up of the .ins file straight out of xprep for diagnosis/debugging 
       
        shutil.copyfile('shelx.ins', home_path + '/backups/' + str(new_folder) + '/' + str(process_counter) + '_shelx_untouched_bu_' + run + '.ins')
        
        structure_INS = New_INS('shelx.ins')
        
        #test to see if ins file is empty or not - if empty, something didn't work 
        
        with open (structure_INS.path, 'rt') as test:
            test_lines = test.readlines()
            if len(test_lines) == 0: 
                XDS_XPREP_status = 'Failed to find a cell from the diffraction data - structure ' + str(counter) + '\n'
                SHELXL_status = 'Did not even get to refinement - structure ' + str(counter) + '\n'
                os.chdir('..')
                with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'a') as report:
                    report.write(XDS_XPREP_status)
                    report.write(SHELXL_status)
                continue    
            else:
                XDS_XPREP_status = 'Successfully created .ins file - structure ' + str(counter) + '\n'
                
        new_SG = structure_INS.space_group        
        
        #For flexible mapping, import structure from reference, if VT and changing symmetry, run SHELXT, if the same as reference, import structure!
        
        if expt_type == 1:
            structure_INS.import_refinement(ref_INS) 
            shutil.copyfile('shelx.ins', home_path + '/backups/' + str(new_folder) + '/' + str(process_counter) + '_shelx_bu_' + run + '.ins')
            
        else:
            if initial_SG == new_SG and no_ref_flag == 0:
                structure_INS.import_refinement(ref_INS)
                shutil.copyfile('shelx.ins', home_path + '/backups/' + str(new_folder) + '/' + str(process_counter) + '_shelx_bu_' + run + '.ins')
            else:
                solve_SHELXT()
                
                #Makes sure if SHELXT did not work, that the code continues onto the next loop before it gets annoyed and throws an error
                
                if 'shelx.ins' not in os.listdir():
                    SHELXT_status = 'SHELXT could not find a solution - structure' + str(counter) + '\n'
                    os.chdir('..')
                    with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'a') as report:
                        report.write(SHELXT_status)
                    continue
                
        #Run SHELXL refinement
        
        refine_SHELXL()   
        
        #Check to see if refinement worked - if didn't, exit before try and make CIFs etc
        
        with open (structure_INS.path, 'rt') as test:
            test_lines = test.readlines()
        if len(test_lines) == 0:
            SHELXL_status = 'Refinement failed - structure ' + str(counter) + '\n'
            os.chdir('..')
            with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'a') as report:
                report.write(XDS_XPREP_status)
                report.write(SHELXL_status)
            continue
        else:
            SHELXL_status = 'Structure successfully refined - structure ' + str(counter) + '\n'
        
        #Edit name of each block to reflect which experiment it is 
        
        with open ('shelx.cif', 'rt') as cif:
            name = []
            lines = cif.readlines()
        for line in lines:
            if 'data_shelx' in line:
                name.append(line.strip('\n').strip('shelx') + str(counter))
        with open ('shelx.cif', 'w') as cif:
            for line in lines:
                if 'data_shelx' in line:
                    cif.write(name[0])
                else:
                    cif.write(line)
                    
        #Calculate the measurement reflections used, theta min and theta max
        
        with open('XPARM.XDS', 'rt') as xparm:
            line_no = 0
            for line in xparm:
                line_no +=1
                if line_no == 9:
                    params = line.split()
            
        A = float(params[0])
        B = float(params[1])
        C = float(params[2])

        with open('SPOT.XDS', 'rt') as spot:
            one = []
            two = []
            for line in spot:
                one.append(float(line.split()[0]))
                two.append(float(line.split()[1]))
        
        tmp = []        
        
        for i in range(0,len(one)):
            tmp.append((math.atan2(math.sqrt(((one[i]-A)*0.075)**2+((two[i]-B)*0.075)**2),108.463135))/2*(180/math.pi))
    
        A = format(min(tmp), '.4f')
        B = format(max(tmp), '.4f')
        C = len(tmp)
        
        #Make more backup files 
        
        shutil.copyfile('XDS_ASCII.HKL', home_path + '/backups/' + str(new_folder) + '/' + str(process_counter) + '_XDS_ASCII_' + str(counter) + '_' + run + '.HKL')
        shutil.copyfile('shelx.cif', home_path + '/backups/' + str(new_folder) + '/' + str(process_counter) + '_shelx_' + run + '.cif')
        
        #Put path to cif in filenames for later access
        
        filenames.append(os.getcwd() + '/edited.cif')
        
        #CIF Editing
        
        cif = ReadCif('shelx.cif')    
        data_block = cif[str(counter)]
        data_block['_chemical_formula_moiety'] = formula
        data_block['_computing_data_collection'] = data_collection
        data_block['_exptl_absorp_correction_type'] = absorp_correction
        data_block['_diffrn_radiation_wavelength'] = wavelength
        data_block['_diffrn_radiation_type'] = radiation_type
        data_block['_diffrn_source'] = radiation_type
        data_block['_diffrn_measurement_device_type'] = detector
        data_block['_diffrn_measurement_method'] = measurement_method
        data_block['_computing_cell_refinement'] = cell_refinement
        data_block['_computing_data_reduction'] = cell_refinement
        data_block['_computing_structure_solution'] = structure_soln
        data_block['_exptl_crystal_colour'] = colour
        data_block['_exptl_crystal_description'] = habit
        data_block['_cell_measurement_temperature'] = temp
        data_block['_diffrn_ambient_temperature'] = temp
        data_block['_exptl_crystal_size_max'] = max_size
        data_block['_exptl_crystal_size_mid'] = mid_size
        data_block['_exptl_crystal_size_min'] = min_size
        data_block['_diffrn_radiation_monochromator'] = monochromator
        data_block['_diffrn_radiation_source'] = source
        data_block['_cell_measurement_reflns_used'] = C
        data_block['_cell_measurement_theta_min'] = A
        data_block['_cell_measurement_theta_max'] = B
        
        with open ('edited.cif', 'w') as updated:
            updated.write(cif.WriteOut())
            
        with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'a') as report:
            report.write(XDS_XPREP_status)
            report.write(SHELXL_status)     
            
        os.chdir('..')   
    
    with open (home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_error_report.txt', 'rt') as report:
        errors = report.readlines()
    
    combined_cif_flag = 0
    
    #Checks error log to see if any of the runs worked - if so, creates a combined cif (combined_cif_flag makes sure process only occurs ONCE)
    
    for line in errors:
        if 'Structure successfully refined' in line and combined_cif_flag == 0:
            with open(str(process_counter) + '_all_cifs.cif', 'w') as combined_cif:
                for expt in filenames:
                    with open(expt) as single_cif:
                        combined_cif.write(single_cif.read())
                    
            shutil.move(home_path + '/analysis/' + str(process_counter) + '_all_cifs.cif', home_path + '/results/' + str(new_folder) + '/' + str(process_counter) + '_all_cifs.cif')
            
            combined_cif_flag += 1
            
    process_counter += 1    
    
    return process_counter
 
 
#This function changes the angles in the XDS.INP file, while also calculating frames/angles based on the total angle/frames and what wedge the user would like to test

def ChangeAngle(total_angle, start_angle, angle):
    angles_to_edit = ['STARTING_ANGLE', 'STARTING_FRAME', 'DATA_RANGE', 'SPOT_RANGE']
    middle_angle = total_angle / 2 + start_angle
    middle_frame = total_angle * 5
    
    if angle == total_angle:
        starting_frame = '1'
        ending_frame = str(angle * 10)
        starting_angle = str(start_angle)
    else:
        number_of_frames = angle * 10
        starting_frame = str(format(middle_frame - (number_of_frames / 2), '.0f'))
        ending_frame = str(format(middle_frame + (number_of_frames / 2), '.0f'))
        starting_angle = str(format(middle_angle - (angle / 2), '.1f'))
      
    XDS_Input.change('STARTING_ANGLE', starting_angle)
    XDS_Input.change('STARTING_FRAME', starting_frame)
    XDS_Input.change('DATA_RANGE', starting_frame + ' ' + ending_frame)
    XDS_Input.change('SPOT_RANGE', starting_frame + ' ' + ending_frame)

#This just changes some common parameters when testing flexible mapping data 

def ChangeParameters(a, b, c, d):
    XDS_Input.change('SPOT_MAXIMUM-CENTROID', a)
    XDS_Input.change('MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT', b)
    XDS_Input.change('STRONG_PIXEL', c)
    XDS_Input.change('SEPMIN', d)


#This function calls the main process_data method in different ways depending on which type of flexible mapping the user wants to do (ie one process, testing wedge angles, or testing XDS.INP Parameters)

def Process_Type(method, process_counter):
    
    #Do this now, because need to change back to original ones in this function
    start_angle, total_angle = XDS_Input.start_angle()
    
    four_values = []
    
    #Single Process - does allow user to define which parameters and what angle to do a single test at 
    
    if method == 0:
        parameters_to_edit = ['SPOT_MAXIMUM-CENTROID', 'MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT', 'STRONG_PIXEL', 'SEPMIN']
        parameter_value = {}
    
        for parameter in parameters_to_edit:
            while True:
                try:
                    value = int(input('Enter a value for ' + parameter + ': '))
                except ValueError:
                    print('Error! Invalid entry')
                else:
                    if value > 0 and value <= 20:
                        break
                    else:
                        print('Something between 2 and 20 is probably best')
                        
            #Appending these values is just for later analysis so the spreadsheet prints out what parameters the test was done under 
            
            four_values.append(value)
            
        tested_spot_MC.append(four_values[0])
        tested_min_pixels.append(four_values[1])
        tested_strong_pixels.append(four_values[2])
        tested_sepmin.append(four_values[3])
            
        ChangeParameters(four_values[0], four_values[1], four_values[2], four_values[3])    
        
        while True:
            try:
                angle = float(input('What angle would you like to test at?: '))
            except ValueError:
                print('Error! Invalid entry')
            else:
                if angle > 0 and angle <= total_angle:
                    tested_angles.append(angle)
                    break
                else:
                    print('Invalid choice')
                
        ChangeAngle(total_angle, start_angle, angle)
        process_counter = process_data(process_counter)
        
        
    #Changing Angles - asks user what angles they want to test, and also asks what single set of parameters to do the tests at 
    
    elif method == 1:
        parameters_to_edit = ['SPOT_MAXIMUM-CENTROID', 'MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT', 'STRONG_PIXEL', 'SEPMIN']
        parameter_value = {}
    
        for parameter in parameters_to_edit:
            while True:
                try:
                    value = int(input('Enter a value for ' + parameter + ': '))
                except ValueError:
                    print('Error! Invalid entry')
                else:
                    if value > 0 and value <= 20:
                        break
                    else:
                        print('Something between 2 and 20 is probably best')
                        
            four_values.append(value)
            
        ChangeParameters(four_values[0], four_values[1], four_values[2], four_values[3])   
         
        while True:
            try: 
                angle = float(input('What angle would you like to test at?(Enter 1000 if you have entered all the angles you wish to test):'))
            except ValueError:
                print('Error! Invalid entry')
            else:
                if angle > 0 and angle <= total_angle:
                    tested_angles.append(angle)
                elif angle == 1000:
                    if len(tested_angles) == 0:
                        print('Please choose an angle')
                    else:
                        break
                else:
                    print('Invalid choice')
                    
        for item in tested_angles:
            ChangeAngle(total_angle, start_angle, item)
            process_counter = process_data(process_counter)
            tested_spot_MC.append(four_values[0])
            tested_min_pixels.append(four_values[1])
            tested_strong_pixels.append(four_values[2])
            tested_sepmin.append(four_values[3])
        
    #Parameter Test - allows user to test a range of parameters at a specified angle, including cases where certain parameters remain unchaged from XDS.INP, or if they want to only test one value for a certain parameter, otherwise a range can be tested
    
    else:
        while True:
            try:
                angle = float(input('What angle would you like to test at?: '))
            except ValueError:
                print('Error! Invalid entry')
            else:
                if angle > 0 and angle <= total_angle:
                    break
                else:
                    print('Invalid choice')
                
        ChangeAngle(total_angle, start_angle, angle)
        
        parameters_to_edit = ['SPOT_MAXIMUM-CENTROID', 'MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT', 'STRONG_PIXEL', 'SEPMIN']
        parameter_value = {}
        
        for parameter in parameters_to_edit:
            
            #the continue flags are there to make sure if the user doesn't want to change, then they are not asked for a range of values 
            
            cont1 = 1
            cont2 = 1
            while True:
                try:
                    para1 = int(input('Minimum [' + parameter + '] (enter 1000 to use value already in XDS.INP): '))
                except ValueError:
                    print('Error! Invalid entry')
                else:
                    if para1 > 0 and para1 <= 20:
                        break
                    elif para1 == 1000:
                        cont1 = 0
                        break
                    elif para1 < 0:
                        print ('Positive Numbers Only')
                    else:
                        print ('That is probably too high and you should reconsider')
            if cont1 == 1:
                while True:
                    try:
                        para2 = int(input('Maximum [' + parameter + ']: (enter 1000 if you do not want to vary this parameter) '))
                    except ValueError:
                        print("Error! Invalid entry")
                    else:
                        if para2 > para1 and para2 <= 21:
                           para2 += 1
                           break
                        elif para2 == 1000:
                            cont2 = 0
                            para3 = 1
                            para2 = para1 + 1
                            break
                        elif para2 < para1:
                            print('Error: maximum smaller than minium')
                        else:
                            print('That is probably too high and you should reconsider')
                if cont2 == 1:               
                    while True: 
                        try:
                            para3 = int(input('[' + parameter + '] Step Size: '))
                        except ValueError:
                            print('Error! Invalid entry')
                        else:
                            if para3 <= (para2 - para1):
                                break
                            else:
                                print('Error! Step size too big')
            else:
                para2 = 0
                para3 = 0
            
            parameter_value[parameter] = [para1, para2, para3]
            
        #Since the term '1000' is currently used as an exit flag, this changes it to the current value in the XDS.INP file
        
        for parameter in parameter_value:
            if parameter_value[parameter][0] == 1000:
                parameter_value[parameter] = [XDS_Input.get_value(parameter)]
            else:
                parameter_value[parameter] = list(range(parameter_value[parameter][0], parameter_value[parameter][1], parameter_value[parameter][2]))
                    
        #Tests all combinations of parameters 
        
        for item1 in parameter_value['SPOT_MAXIMUM-CENTROID']:
            for item2 in parameter_value['MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT']:
                for item3 in parameter_value['STRONG_PIXEL']:
                    for item4 in parameter_value['SEPMIN']:
                        tested_spot_MC.append(item1)
                        tested_min_pixels.append(item2)
                        tested_strong_pixels.append(item3)
                        tested_sepmin.append(item4)
                        tested_angles.append(angle)
                        ChangeParameters(item1, item2, item3, item4)
                        process_counter = process_data(process_counter)
   
    #Resets back to starting details
        
    XDS_Input.change("STARTING_ANGLE", start_angle)
    XDS_Input.change("STARTING_FRAME", 1)
    XDS_Input.change("DATA_RANGE", "1 " + str(total_angle * 10))
    XDS_Input.change("SPOT_RANGE", "1 " + str(total_angle * 10))
    
    
#This function steps through the analysis for flexible mapping experiments 

def Flexible_Analysis(df_cell_parameters):
    run_file = []
    cif_count = 1
    cif_count2 = 0
    angles_final = []
    spot_MC_final = []
    min_pixels_final = []
    strong_pixel_final = []
    sepmin_final = []

    #Include CIF name, position number and distance in the dataframe - cycles through based on the number of structures per cif found from the CIF class 

    for i in structures_per_cif:
        while cif_count <= i:
            run_file.append(cif_names[cif_count2])
            angles_final.append(tested_angles[cif_count2])
            spot_MC_final.append(tested_spot_MC[cif_count2])
            min_pixels_final.append(tested_min_pixels[cif_count2])
            strong_pixel_final.append(tested_strong_pixels[cif_count2])
            sepmin_final.append(tested_sepmin[cif_count2])
            cif_count += 1
        cif_count2 += 1
        cif_count = 1

    #Adds to dataframe 
    
    df_cell_parameters['CIF Name'] = run_file
    df_cell_parameters['Wedge Angle'] = angles_final
    df_cell_parameters['Spot Maximum-Centroid'] = spot_MC_final
    df_cell_parameters['Minimum Number of Pixels in a Spot'] = min_pixels_final
    df_cell_parameters['Strong Pixel'] = strong_pixel_final
    df_cell_parameters['Sepmin'] = sepmin_final

    list_of_runs = []
    previous_run = ''

    #This goes through each compiled cif and looks at the data_block names so that the run numbers correlate with the experiment numbers 
    
    for i in run_file:
        if previous_run != i:
            cif = ReadCif(i)
            for j in range(0, number_of_runs + 1):
                try:
                    data_block = cif[str(j)]
                except KeyError:
                    pass
                else:
                    list_of_runs.append(j)
        previous_run = i
            
    df_cell_parameters['Position Number'] = list_of_runs   

    #Calculates the distance moved based on the user inputted step size 
    
    distance_moved = [x * step_size for x in list_of_runs]

    df_cell_parameters['Distance'] = distance_moved

    #Calculate cell deformations
        
    df_cell_deformations = pd.DataFrame()
        
    df_cell_deformations['a_axis_deformation'] = ((df_cell_parameters['a_axis'] / ref_INS.a) -1) *100
    df_cell_deformations['b_axis_deformation'] = ((df_cell_parameters['b_axis'] / ref_INS.b) -1) *100  
    df_cell_deformations['c_axis_deformation'] = ((df_cell_parameters['c_axis'] / ref_INS.c) -1) *100
    df_cell_deformations['volume_deformation'] = ((df_cell_parameters['volume'] / ref_INS.volume) -1) *100
    df_cell_deformations['CIF Name'] = run_file
    df_cell_deformations['Position Number'] = list_of_runs
    df_cell_deformations['Distance'] = distance_moved
    df_cell_deformations['Wedge Angle'] = angles_final
    df_cell_deformations['Spot Maximum-Centroid'] = spot_MC_final
    df_cell_deformations['Minimum Number of Pixels in a Spot'] = min_pixels_final
    df_cell_deformations['Strong Pixel'] = strong_pixel_final
    df_cell_deformations['Sepmin'] = sepmin_final

    #Output combined CSV Files
            
    df_cell_parameters.to_csv('Unit_Cell_Parameters_ALL.csv', index = None)
    df_cell_deformations.to_csv('Unit_Cell_Deformations_ALL.csv', index = None)  

    #Compare Statistics by first separating dataframes by angle (combined graph only applicable for angle changing test - will still plot individual ones for single/parameter changing tests) 

    if method == 1:
        
        separated_by_angle_dfs = []

        for item in tested_angles:
            condition = df_cell_parameters['Wedge Angle'] == item
            separated_by_angle_dfs.append(df_cell_parameters[condition])
            
        cif_index = 0   
            
        #Plots all of the Rints and completeness on one graph and saves to a .png file 
        
        for item in separated_by_angle_dfs:
            x = item['Distance']
            rint = item['Rint']
            completeness = item['Completeness']
            
            plt.scatter(x, rint, label = 'Rint at Angle ' + str(item.iloc[0]['Wedge Angle']))
            plt.scatter(x, completeness, label = 'Completeness at Angle ' + str(item.iloc[0]['Wedge Angle']))
            plt.xlabel('Distance($\mu$m)', fontsize = 12)
            plt.title('Overall Data Statistics')
            plt.legend(fontsize = 12)
            cif_index += 1
            
        figure = plt.gcf()
        figure.set_size_inches(16,12)
            
        plt.savefig('Overall Data Statistics' + '.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()  
       
    #Separate dataframes/deformations by cif file

    separated_dfs = []
    separated_dfs_deformations = []

    for item in cif_names:
        condition = df_cell_parameters['CIF Name'] == item
        condition_def = df_cell_deformations['CIF Name'] == item
        separated_dfs.append(df_cell_parameters[condition])
        separated_dfs_deformations.append(df_cell_deformations[condition_def])
        
    cif_index = 0

    #For each separated dataframe, plots the statistics and deformations and outputs to separate .png files 
    
    for item in separated_dfs:
        item.to_csv(cif_names[cif_index].strip('.cif') + '_parameters.csv', index = None)
        
        x = item['Distance']
        rint = item['Rint']
        completeness = item['Completeness']
        
        plt.scatter(x, rint, label = 'Rint')
        plt.scatter(x, completeness, label = 'Completeness')
        plt.xlabel('Distance($\mu$m)', fontsize = 12)
        plt.title(cif_names[cif_index] + ' Data Statistics')
        plt.legend(fontsize = 12)
        
        figure = plt.gcf()
        figure.set_size_inches(16,12)
        
        plt.savefig('Data Statistics of ' + cif_names[cif_index].strip('.cif') + '.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()
        
        cif_index += 1

    cif_index = 0
        
    for item in separated_dfs_deformations:
        item.to_csv(cif_names[cif_index].strip('.cif') + '_deformations.csv', index = None)
        
        x = item['Distance']
        a_def = item['a_axis_deformation']
        b_def = item['b_axis_deformation']
        c_def = item['c_axis_deformation']
        vol_def = item['volume_deformation']
        
        plt.scatter(x, a_def, c = 'red', marker = 'x', linewidth = 1, s = 100, label = '$\epsilon$ a-axis')
        plt.scatter(x, b_def, c = 'green', marker = '+', linewidth = 1, s = 100, label = '$\epsilon$ b-axis')
        plt.scatter(x, c_def, c = 'blue', marker = '$*$', linewidth = 0.5, s = 200, label = '$\epsilon$ c-axis')
        plt.scatter(x, vol_def, c = 'black', marker = '.', linewidth = 0.75, s = 100, label = '$\epsilon$ volume')
        
        plt.xlabel('Distance ($\mu$m)', fontsize = 12)
        plt.ylabel('Deformation (%)', fontsize = 12)
        plt.title(cif_names[cif_index] + ' Deformations')
        plt.legend(fontsize = 12)
        
        figure = plt.gcf()
        figure.set_size_inches(16,12)
        
        plt.savefig('Deformation of ' + cif_names[cif_index].strip('.cif') + '.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()
        
        cif_index += 1
        
#This function does analysis for VT experiments 

def VT_Analysis(df_cell_parameters):
    index = 0
    behaviour = []
    data = df_cell_parameters['temperature']
    
    #Searches through the data and classifies everything as a temperature minima, maxima, increasing or decreasing 
    
    for i in data:
        if index != 0 and index != len(data) - 1:
            if i < data[index-1] and i < data[index+1]:
                behaviour.append('Minima')
            elif i > data[index-1] and i > data[index+1]:
                behaviour.append('Maxima')
            elif i < data[index-1] and i > data[index+1]:
                behaviour.append('Decreasing')
            elif i > data[index-1] and i < data[index+1]:
                behaviour.append('Increasing')
        
        #This else statement is needed to classify the first and last points 
        
        else:
            if index == 0:
                if i < data[index+1]:
                    behaviour.append('Increasing')
                else:
                    behaviour.append('Decreasing')
            else:
                if i < data[index-1]:
                    behaviour.append('Decreasing')
                else:
                    behaviour.append('Increasing')
        index += 1
        
    df_cell_parameters['behaviour'] = behaviour
    
    #Remove duplicates
    
    discrete_behaviour = list(dict.fromkeys(behaviour))
    
    separated_by_behaviour_dfs = []
    
    #Separates the dataframe by behaviour, then plots them all on the same graph so they have different colours depending on the behaviour of the temperature at that point 
    
    for item in discrete_behaviour:
        condition = df['behaviour'] == item
        separated_by_behaviour_dfs.append(df[condition])
        
    df_cell_parameters.to_csv('Unit_Cell_Parameters.csv', index = None)
        
    index = 0    
    
    for item in separated_by_behaviour_dfs:
        x = item['temperature']
        y1 = item['a_axis']
        y2 = item['b_axis']
        y3 = item['c_axis']
        y4 = item['alpha']
        y5 = item['beta']
        y6 = item['gamma']
        y7 = item['volume']
        
        ax1 = plt.subplot(2, 4, 1)
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y1, label = 'a axis ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('a-axis')
        plt.legend()
        
        ax2 = plt.subplot(2, 4, 2)
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax2.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y2, label = 'b axis ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('b-axis')
        plt.legend()
        
        ax3 = plt.subplot(2, 4, 3)
        ax3.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax3.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y3, label = 'c axis ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('c-axis')
        plt.legend()
        
        ax4 = plt.subplot(2, 4, 5)
        ax4.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax4.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y4, label = 'alpha ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('alpha')
        plt.legend()
        
        ax5 = plt.subplot(2, 4, 6)
        ax5.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax5.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y5, label = 'beta ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('beta')
        plt.legend()
        
        ax6 = plt.subplot(2, 4, 7)
        ax6.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax6.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y6, label = 'gamma ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('gamma')
        plt.legend()
        
        ax7 = plt.subplot(2, 4, 8)
        ax7.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax7.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y4, label = 'volume ' + discrete_behaviour[index])
        plt.xlabel('Temperature(K)')
        plt.ylabel(u'Volume (\u212B\u00B3)')
        plt.title('volume')
        plt.legend()
        
        index += 1
        
    figure = plt.gcf()
    figure.set_size_inches(16,12)
    plt.savefig('Variable_Temperature_Analysis.png', bbox_inches = 'tight', dpi = 100)
    plt.clf()
    
    
#----------Proceedure Starts Here----------#    

    
#Initial Greeting!

print('Welcome to the Automated Analysis of Large Crystallographic Data Sets!')
print('Please answer a few questions to start with so that you can be provided with finalised CIF files at the end of this.')

#Setting up required variables

home_path = os.getcwd()
ref_path = home_path + '/ref/ref.ins'
XDS_INP = home_path + '/input/XDS.INP'


while True:
    try:
        beamline = input('Are you using the MX1 beamline or the MX2 beamline?: ')
    except:
        print('Error!')
    else:
        if beamline.upper() == 'MX1':
            data_collection = MX1_data_collection
            absorp_correction = MX1_absorp_correction 
            radiation_type = MX1_radiation_type
            measurement_method = MX1_measurement_method
            cell_refinement = MX1_cell_refinement
            structure_soln = MX1_structure_soln 
            monochromator = MX1_monochromator
            source = MX1_source 
            detector = MX1_detector 
            break
        elif beamline.upper() == 'MX2':
            data_collection = MX2_data_collection
            absorp_correction = MX2_absorp_correction 
            radiation_type = MX2_radiation_type
            measurement_method = MX2_measurement_method
            cell_refinement = MX2_cell_refinement
            structure_soln = MX2_structure_soln 
            monochromator = MX2_monochromator
            source = MX2_source 
            detector = MX2_detector 
            break
        else:
            print('Error! Please select (MX1) or (MX2)')

#Looks to see if CIF data already there or not (so can close program and NOT have to re-input information!)

try:
    CIF_data = pd.read_csv(home_path + '/ref/cif_info.csv')
except FileNotFoundError:
    habit, colour, max_size, mid_size, min_size = CIF_finalisation_questions()
    cif_df = pd.DataFrame()
    cif_df['habit'] = [habit]
    cif_df['colour'] = [colour]
    cif_df['max_size'] = [max_size]
    cif_df['mid_size'] = [mid_size]
    cif_df['min_size'] = [min_size]
    cif_df.to_csv(home_path + '/ref/cif_info.csv', index = None)
           
else:
    t1 = CIF_data['habit']
    t2 = CIF_data['colour']
    t3 = CIF_data['max_size']
    t4 = CIF_data['mid_size']
    t5 = CIF_data['min_size']
    
    habit = t1.to_string(index=False)
    colour = t2.to_string(index=False)
    max_size = t3.to_string(index=False)
    mid_size = t4.to_string(index=False)
    min_size = t5.to_string(index=False)
    
    print('Crystal habit = ' + habit + ', crystal colour = ' + colour + ', crystal dimensions = ' + max_size + 'x' + mid_size + 'x' + min_size)
    
    while True:
        try:
            parameter_flag = input('Are these details correct? Enter Y for yes or N for no: ')
        except:
            print('Error! Please try again')
        else:
            if parameter_flag.upper() == 'N':
                habit, colour, max_size, mid_size, min_size = CIF_finalisation_questions()
                cif_df = pd.DataFrame()
                cif_df['habit'] = [habit]
                cif_df['colour'] = [colour]
                cif_df['max_size'] = [max_size]
                cif_df['mid_size'] = [mid_size]
                cif_df['min_size'] = [min_size]
                cif_df.to_csv(home_path + '/ref/cif_info.csv', index = None)
                break
            elif parameter_flag.upper() == 'Y':
                break
            else:
                print('Error! Please try again')

#Need to know which angles and which parameters to display with output data

tested_angles = []
tested_spot_MC = []
tested_min_pixels = []
tested_strong_pixels = []
tested_sepmin = []
list_of_runs = []

#Need to number the experiments as we go through for appropriate naming of CIF files (This is equal to the number of times a full dataset is processed - so for tests where parameters and angles are changing, this value will be equal to the number of parameter combinations tested

process_counter = 1

#Variables which need to be pulled from somewhere (temporarily assigned here)

temp = '100(2)'
formula = 'C10 H12 O4 Cl2 Pd'
#SG = 'P2(1)/n'
SG_no = 14

#To decide flow of the code
print('Thank you for that information! Now for the most important question... are you analysing Flexible Crystal Data or Variable Temperature Data?')

while True:
    try:
        expt_type = int(input('Enter 1 for Flexible Crystal Mapping, or enter 2 for Variable Temperature Analysis: '))
    except ValueError:
        print('Error! That was not a number!')
    else:
        if expt_type == 1 or expt_type == 2:
            break
        else:
            print('Error! Please select (1) or (2)')
            
if expt_type == 1:
    while True:
        try:
            step_size = int(input('Enter step size used (in micro-metres): '))
        except ValueError:
            print('Error! That was not a number!')
        else:
            if step_size > 0 and step_size < 10:
                break
            else:
                print('Are you sure this was a mapping experiment?')
                
#Organise Folders and Files IF this hasn't been done for a previous analysis

if not os.path.exists('analysis'):
    os.mkdir('analysis')
    os.mkdir('ref')
    os.mkdir('input')
    os.mkdir('results')
    os.mkdir('frames')
    os.mkdir('backups')
    
    for files in os.listdir(home_path):
        if files.endswith('master.h5'):
            b = files.replace('_master.h5', '')
            os.mkdir('analysis/' + b)
    
    os.chdir('analysis')
    
    for folder in os.listdir():
        os.symlink(home_path + '/frames', folder + '/img')
        if expt_type == 1:
        
            #Will only have these files for flexible crystal analysis 
        
            shutil.copy(home_path + '/GAIN.cbf', folder)
            shutil.copy(home_path + '/BKGINIT.cbf', folder)
            shutil.copy(home_path + '/BLANK.cbf', folder)
            shutil.copy(home_path + '/X-CORRECTIONS.cbf', folder)
            shutil.copy(home_path + '/Y-CORRECTIONS.cbf', folder)
        
    os.chdir('..')
    
    for files in os.listdir(home_path):
        if files.endswith(('.cbf', '.ins', '.XDS')):
            shutil.move(home_path + '/' + files, home_path + '/ref/' + files)
        elif files.endswith('.INP'):
            shutil.move(home_path + '/' + files, home_path + '/input/' + files)
        elif files.endswith('.h5'):
            shutil.move(home_path + '/' + files, home_path + '/frames/' + files)
            
#Setting up folders to distinguish - this number goes up by 1 every time the entire code is run (to keep everything organised)
    
os.chdir(home_path + '/backups/')
tmp = os.listdir()
tmp2 = []
for item in tmp:
    tmp2.append(int(item))
tmp2.sort()

try:
    new_folder = int(tmp2[-1]) + 1
    
except IndexError:
    new_folder = 1    
        
os.mkdir(home_path + '/backups/' + str(new_folder))
os.mkdir(home_path + '/results/' + str(new_folder))
os.chdir(home_path)
            
#Set up file objects and edit files - only reads in instrument parameters for mapping analysis as this isn't relevant for VT stuff 

if expt_type == 1:
    XDS_Input = Flexible_Mapping_XDS_Input_File(XDS_INP)
    with open (home_path + '/ref/GXPARM.XDS', 'rt') as instrument:
        line_counter = 0
        for line in instrument:
            line_counter += 1
            if line_counter == 9:
                data = line.strip('\n').split(' ')
    data2 = []            
    for element in data:
        if '.' in element:
            data2.append(element)
    orgx = data2[0]
    orgy = data2[1]
    dist = data2[2]

    XDS_Input.change('ORGX', orgx)
    XDS_Input.change('ORGY', orgy)
    XDS_Input.change('DETECTOR_DISTANCE', dist)
    
else:
    XDS_Input = Variable_Temperature_XDS_Input_File(XDS_INP)



#This section looks for the reference structure and uses it to create an INS file object if applicable
#If no file named 'ref.ins' is present, the program will look for other ins files and ask the user if they are the reference and rename it
#This currently only works for ONE reference - if go with the multiple reference idea will need to change this

no_ref_flag = 2

if 'ref.ins' in os.listdir(home_path + '/ref'):
    ref_INS = Reference_INS(ref_path)
    XDS_Input.change('UNIT_CELL_CONSTANTS', str(ref_INS.a) + ' ' + str(ref_INS.b) + ' ' + str(ref_INS.c) + ' ' + str(ref_INS.alpha) + ' ' + str(ref_INS.beta) + ' ' + str(ref_INS.gamma))  
    SG = ref_INS.space_group
    no_ref_flag = 0
    
else:    
    for files in os.listdir(home_path + '/ref'):  
        if files.endswith('.ins') and no_ref_flag != 0:
            while True:
                try:
                    other_named_ref = input('Is ' + files + ' your reference structure? Enter Y for yes or N for no: ')
                except:
                    print('Error!')
                else:
                    if other_named_ref.upper() == 'Y':
                        os.rename(home_path + '/ref/' + files, home_path + '/ref/ref.ins')
                        ref_INS = Reference_INS(ref_path)
                        no_ref_flag = 0
                        XDS_Input.change('UNIT_CELL_CONSTANTS', str(ref_INS.a) + ' ' + str(ref_INS.b) + ' ' + str(ref_INS.c) + ' ' + str(ref_INS.alpha) + ' ' + str(ref_INS.beta) + ' ' + str(ref_INS.gamma))  
                        SG = ref_INS.space_group
                        break
                    elif other_named_ref.upper() == 'N':
                        no_ref_flag = 1
                        break
                    
    if no_ref_flag == 1:
        print('No Reference structure provided. Are you sure you want to continue? Automatic structure solutions may not be reliable: issues include incorrect symmetry, missing atoms, mis-assigned atoms, etc - check all data prior to publication.')
        while True:
            try:
                flag = int(input('Enter 1 to continue: '))
            except ValueError:
                print('Error! Invalid entry')
            else:
                if flag == 1:
                    break
                else:
                    print('Error! Please enter 1 to continue, or exit the program')
    


#Additional variable setting up

wavelength = XDS_Input.get_value('X-RAY_WAVELENGTH')
XDS_Input.change('SPACE_GROUP_NUMBER', SG_no)

os.chdir('analysis')

if expt_type == 1:
    print('Set up complete. What type of analysis would you like done?')

    while True:
        try:
            method = int(input('Enter 0 to process a single dataset, 1 to test wedge angles, or 2 to test various parameters: '))
        except ValueError:
            print('Error! That was not a number...')
        else:
            if method in range(0,3):
                break
            else:
                print('Invalid choice')
                
else:
    method = 0
    print('Set up complete. Beginning Analysis.')

    
Process_Type(method, process_counter)
            
    
#----------Analysis----------#    

    
#Seting up a variable for later use (in the Flexible_Analysis function)

os.chdir(home_path + '/analysis')
number_of_runs = 0
for run in os.listdir():
    number_of_runs += 1

os.chdir(home_path + '/results/' + str(new_folder))

#Gathering cell parameters and combined output data files      
      
index = 0

desired_parameters = ["_cell_length_a", "_cell_length_b", "_cell_length_c", "_cell_angle_alpha", "_cell_angle_beta", "_cell_angle_gamma", "_cell_volume", "_cell_measurement_temperature", "_diffrn_reflns_av_R_equivalents", "_diffrn_measured_fraction_theta_full"]                              
objects = [Cell_Parameter(i) for i in desired_parameters]
structures_per_cif, cif_names = objects[0].data()[2:4]
df_cell_parameters = pd.DataFrame()
    
for i in objects[0:8]:
    df_cell_parameters[index], df_cell_parameters[index+1] = i.data()[0:2]
    index += 2
for i in objects[8:10]:
    df_cell_parameters[index] = i.data()[0]  
    index += 1
    
#Combined dataframe     
        
df_cell_parameters.columns = ['a_axis', 'a_axis_error', 'b_axis', 'b_axis_error', 'c_axis', 'c_axis_error', 'alpha', 'alpha_error', 'beta', 'beta_error', 'gamma', 'gamma_error', 'volume', 'volume_error', 'temperature', 'temperature_error', 'Rint', 'Completeness']  

if expt_type == 1:
    Flexible_Analysis(df_cell_parameters)
else:
    VT_Analysis(df_cell_parameters)   


























    
    
    


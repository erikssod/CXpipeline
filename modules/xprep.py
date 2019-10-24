#!/usr/bin/env python3

#----------Required Modules----------#


import subprocess
import yaml
import logbook
import sys 
import os
 
 
class XPREP:
    def __init__(self, home_path, structure_number = 1):
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
                
        self.reference = self.cfg['reference_provided']
        self.formula = self.cfg['chemical_formula']
        self.space_group = self.cfg['space_group']
        if self.cfg['second_space_group'] != '':
            self.second_space_group = self.cfg['second_space_group']
                
    #A procedure to accept whatever xprep thinks - equivalent to a person sitting there and just pressing enter for everything    
  
    def run_XPREP_auto(self):
        xprep = subprocess.Popen(['xprep'], stdin = subprocess.PIPE, encoding='utf8')
        xprep.stdin.write('XDS_ASCII.HKL_p1\n')
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
        xprep.stdin.write(self.formula + '\n')
        xprep.stdin.write('E\n')
        xprep.stdin.write('F\n')
        xprep.stdin.write('shelx\n')
        xprep.stdin.write('S\n')
        xprep.stdin.write('Y\n')
        xprep.stdin.write('\n')
        xprep.stdin.write('Q\n')
        xprep.stdin.close()
        xprep.wait()
        
    #A procedure to run XPREP based on a known space group and chemical formula
 
    def run_XPREP_known(self):
        xprep = subprocess.Popen(['xprep'], stdin = subprocess.PIPE, encoding='utf8')
        xprep.stdin.write('XDS_ASCII.HKL_p1\n')
        xprep.stdin.write('X\n')
        xprep.stdin.write('Y\n')
        xprep.stdin.write('P\n')
        xprep.stdin.write('U\n')
        xprep.stdin.write('O\n')
        xprep.stdin.write('1 0 0 0 1 0 0 0 1\n')
        xprep.stdin.write('S\n')
        xprep.stdin.write('I\n')
        xprep.stdin.write(self.space_group + '\n')
        xprep.stdin.write('Y\n')
        xprep.stdin.write('D\n')
        xprep.stdin.write('S\n')
        xprep.stdin.write('A\n')
        xprep.stdin.write('\n')
        xprep.stdin.write('E\n')
        xprep.stdin.write('C\n')
        xprep.stdin.write(self.formula + '\n')
        xprep.stdin.write('E\n')
        xprep.stdin.write('F\n')
        xprep.stdin.write('shelx\n')
        xprep.stdin.write('S\n')
        xprep.stdin.write('Y\n')
        xprep.stdin.write('\n')
        xprep.stdin.write('Q\n')
        xprep.stdin.close()
        xprep.wait()
            

    













    
    
    


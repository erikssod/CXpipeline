#!/usr/bin/env python3

####################################################################################
#--------------------------CX-ASAP: file_setup_autoprocess-------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#This module will set up the file system based purely on the results of the Australian Synchrotron's Autoprocessing pipeline 

#If run from the synchrotron's data system, run from experiment\home\researcher\auto\dataset

#Otherwise, have all folders of data in one master folder 

#Whilst is set up to be stand alone, generally not useful on its own unless wishing to step through processes one at a time?

#WARNING: This will delete any previously made .ins files - make sure reference is in alternate location and be prepared to lose any test files 

#----------Required Modules----------#

import os 
import shutil
import yaml
import logbook
import pathlib

#----------Class Definition----------#

class Setup():
    def __init__(self, original_path = os.getcwd()):
        
        #Set up logbook and config file 
        
        logbook.FileHandler(original_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        self.conf_path = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent / 'conf.yaml'
        
        with open (self.conf_path, 'r') as f:
            try: 
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
        self.original_path = original_path
        self.home = self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis'
        self.tree_structure = ['analysis', 'ref', 'results', 'failed_autoprocessing']
        
        if pathlib.Path(self.original_path).stem == self.home:
            self.home_path = self.original_path
        else:
            self.home_path = os.path.join(self.original_path, self.home)
                    
        self.analysis_path = os.path.join(self.home_path, self.tree_structure[0])
        self.ref_path = os.path.join(self.home_path, self.tree_structure[1])
        self.results_path = os.path.join(self.home_path, self.tree_structure[2])
        self.failed_path = os.path.join(self.home_path, self.tree_structure[3])    
                     
        self.cfg['home_path'] = self.home_path
        self.cfg['analysis_path'] = self.analysis_path
        self.cfg['ref_path'] = self.ref_path
        self.cfg['results_path'] = self.results_path
        self.cfg['failed_path'] = self.failed_path  
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f)
        
    def Organise_Directory_Tree(self):
        
        #Most of this is only run if it has not already been set up
        
        if not os.path.exists(self.home_path):
            os.mkdir(self.home)
            os.chdir(self.home_path)
            for item in self.tree_structure:
                os.mkdir(item)
            
        #Move structure reference into the ref folder 
        
            try:
                shutil.copy(self.cfg['reference_path'], self.ref_path)
            except FileNotFoundError as error:
                self.logger.info(f'Failed to find reference file with error {error}')
                
            if self.cfg['second_reference_path'] != '':
                try:
                    shutil.copy(self.cfg['second_reference_path'], self.ref_path)
                except FileNotFoundError as error:
                    self.logger.info(f'Failed to find second reference file with error {error}')

            os.chdir('..')
        
            
            #Moves everything into the analysis folder
            
            for item in os.listdir():
                if self.cfg['file_name'] in item:
                    if 'analysis' not in item:
                        shutil.move(item, os.path.join(self.analysis_path, item))
                        
            os.chdir(self.analysis_path)
            
            shutil.move(os.path.join(self.original_path, 'error_output.txt'), os.path.join(self.home_path, 'error_output.txt'))
        
            #Finds out which runs failed to autoprocess and moves them to the failed folder
            
            for run in os.listdir():
                if os.path.isdir(run):
                    os.chdir(run)
                    if 'autoprocess.cif' not in os.listdir():
                        shutil.move(os.path.join(self.analysis_path, run), os.path.join(self.failed_path, run))
                        self.logger.info('Synchrotron failed to autoprocess - run ' + run)
                    else:
                        self.logger.info('Synchrotron autoprocessed successfully - run ' + run)
                    os.chdir('..')
                    
            #This next part adds numbers so folders are correctly ordered
                
            #Also allows for the fact that if the screenings auto-process they will be present too 
            
            os.chdir(self.analysis_path)
            
            list_split = []
            data_dict = {}
            data = []
                
            for item in os.listdir():
                if os.path.isdir(item):
                    list_split.append(item.split('_'))
                    data.append(item)
            index = 0
                
            for item in list_split:
                data_dict[item[-3]] = []
            for item in list_split:
                data_dict[item[-3]].append(index)
                index += 1
                    
            keys = sorted(data_dict.keys())
                
            counter = 1
                
            for key in keys:
                for value in data_dict[key]:
                    os.rename(data[value], str(counter) + '_' + data[value])
                    counter += 1
                    
        os.chdir(self.results_path)
        
        #Makes a new folder in the results for each time the code is run - keeps tests separated 
        
        tmp = os.listdir()
        tmp2 = []
        for item in tmp:
            if os.path.isdir(item):
                tmp2.append(int(item))
        tmp2.sort()
        
        try:
            self.new_folder = int(tmp2[-1]) + 1
        except IndexError:
            self.new_folder = 1
            
        os.mkdir(os.path.join(self.results_path, str(self.new_folder)))
        
        self.cfg['current_results_path'] = (os.path.join(self.results_path, str(self.new_folder)))
        self.cfg['ref_ins_path'] = os.path.join(self.ref_path, pathlib.Path(self.cfg['reference_path']).name)
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f)
        
        #Gets rid of all .ins files from the analysis folders to make sure that the code runs ok later
        
        os.chdir(self.analysis_path)
        
        for run in os.listdir():
            if os.path.isdir(run):
                os.chdir(run)
                for item in os.listdir():
                    if '.ins' in item:
                        os.remove(item)
                os.chdir('..')
        
        os.chdir(self.home_path)
        
#If the code is called individually from the commandline, the below code runs the required functions 
                    
if __name__ == "__main__":
    initialisation = Setup()
    initialisation.Organise_Directory_Tree()
        

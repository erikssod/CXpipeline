#!/usr/bin/env python3

####################################################################################
#-------------------------CX-ASAP: file_setup_reprocessing-------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#This module will set up the file system for reprocessing, meaning the frames are isolated 

#If run from the synchrotron's data system, run from experiment\frames\researcher\dataset

#Otherwise, have all folders of frames in one master location 

#Whilst is set up to be stand alone, generally not useful on its own unless wishing to step through processes one at a time?


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
                
        #Setting up the various paths and saving to config file
               
        self.original_path = original_path
        self.home = self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis'
        self.tree_structure = ['analysis', 'ref', 'results', 'frames']
        
        if pathlib.Path(self.original_path).stem == self.home:
            self.home_path = self.original_path
        else:
            self.home_path = os.path.join(self.original_path, self.home)
                    
        self.analysis_path = os.path.join(self.home_path, self.tree_structure[0])
        self.ref_path = os.path.join(self.home_path, self.tree_structure[1])
        self.results_path = os.path.join(self.home_path, self.tree_structure[2])
        self.frames_path = os.path.join(self.home_path, self.tree_structure[3])    
                     
        self.cfg['home_path'] = self.home_path
        self.cfg['analysis_path'] = self.analysis_path
        self.cfg['ref_path'] = self.ref_path
        self.cfg['results_path'] = self.results_path
        self.cfg['frames_path'] = self.frames_path  
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f)
                
    def move_frames(self, files, run):
        
        #Put into a function to minimise repetition, and makes the run folders with consistent naming system based on the frames 
        
        if files.endswith('master.h5'):
            b = files.replace('_master.h5', '')
            os.mkdir(os.path.join(self.analysis_path, b))
        if files.endswith('.h5'):
            shutil.move(os.path.join(self.frames_path, run, files), os.path.join(self.frames_path, files))

    
    def Organise_Directory_Tree(self):
        
        #Most of this is only run if it has not already been set up
        
        if not os.path.exists(self.home_path):
            os.mkdir(self.home)
            os.chdir(self.home_path)
            
            #Make all folders from tree structure
            
            for item in self.tree_structure:
                os.mkdir(item)
                
            #Move structure reference and XDS.INP into the ref folder 
             
            try:
                shutil.copy(self.cfg['reference_path'], self.ref_path)
            except FileNotFoundError as error:
                self.logger.info(f'Failed to find reference file with error {error}')
                
            try:
                shutil.copy(self.cfg['xds_reference_path'], self.ref_path)
            except FileNotFoundError as error:
                self.logger.critical(f'Failed to find reference XDS.INP with error {error}')
                exit()
                
            os.chdir('..')
            
            #Moves everything into the analysis folder 
            
            for item in os.listdir():
                if self.cfg['file_name'] in item:
                    if 'analysis' not in item:
                        shutil.move(item, os.path.join(self.frames_path, item))
            
            os.chdir(self.frames_path)
            
            #Moves all frames into the frames folder and tidies up empty folders 
            
            for run in os.listdir():
                if os.path.isdir(run):
                    os.chdir(run)
                    for files in os.listdir():
                        self.move_frames(files, run)
                    os.chdir('..')
                    shutil.rmtree(run)
                else:
                    self.move_frames(files, run)
                    
            os.chdir(self.analysis_path)
            
            #Creates symbolic link in every run to the frames folder 
            
            for folder in os.listdir():
                os.symlink(self.frames_path, os.path.join(folder, 'img'))
                    
        os.chdir(self.results_path)
        
        #Makes a new folder in the results for each time the code is run - keeps tests separated 
        
        tmp = os.listdir()
        tmp2 = []
        for item in tmp:
            tmp2.append(int(item))
        tmp2.sort()
        
        try:
            self.new_folder = int(tmp2[-1]) + 1
        except IndexError:
            self.new_folder = 1
            
        os.mkdir(os.path.join(self.results_path, str(self.new_folder)))
        
        self.cfg['current_results_path'] = (os.path.join(self.results_path, str(self.new_folder)))
        
        os.chdir(self.home_path)
        
        #Moves the error_output file into home_path 
        
        shutil.move(os.path.join (self.original_path, 'error_output.txt'), os.path.join (self.home_path, 'error_output.txt'))
        
        self.cfg['XDS_INP_path'] = os.path.join(self.ref_path, 'XDS.INP')
        self.cfg['ref_ins_path'] = os.path.join(self.ref_path, pathlib.Path(self.cfg['reference_path']).name)
        
        with open (self.conf_path, 'w') as f:
            yaml.dump(self.cfg, f)
        
#If the code is called individually from the commandline, the below code runs the required functions 
                    
if __name__ == "__main__":
    initialisation = Setup()
    initialisation.Organise_Directory_Tree()

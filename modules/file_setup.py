#!/usr/bin/env python3

import os
import shutil
import logbook
import yaml


class Setup():
    def __init__(self):
        
        #Set up logbook and config file 
        
        self.home_path = os.getcwd()
        self.original_path = os.getcwd()
        
        logbook.FileHandler(self.home_path + '/error_output.txt', 'a').push_application()  
        self.logger = logbook.Logger(self.__class__.__name__)
        logbook.set_datetime_format("local")
        self.logger.info('Class Initialised!')
        
        with open('/usr/local/bin/scripts/conf.yaml', 'r') as f:
            try:
                self.cfg = yaml.load(f)
            except yaml.YAMLERROR as error:
                self.logger.critical(f'Failed to open config file with {error}')
                exit()
                
    #Helpful for sorting things properly 
                
    def sorted_properly(self, data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    #Will mostly be for flexible crystals
    
    def Organise_Directory_Reprocessing(self):
        if not os.path.exists(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis') and not os.path.exists('analysis'): 
        
            os.mkdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            
            #User defines where they have their reference (assuming while at the synchrotron they did one up)
            #So before change all of the folders to make neat and tidy, first need to copy the reference from that location
            
            os.chdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            
            tree_structure = ['analysis', 'ref', 'results', 'frames']
            
            for item in tree_structure:
                os.mkdir(item)
                
            os.chdir('..')
            
            try:
                shutil.copy(self.cfg['reference_path'], self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis/ref')
            except FileNotFoundError as error:
                self.logger.info(f'Failed to find reference file with error {error}')
                
            try:
                shutil.copy(self.cfg['xds_reference_path'], self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis/ref')
            except FileNotFoundError as error:
                self.logger.critical(f'Failed to find reference XDS.INP with error {error}')
                exit()
                
            try:
                shutil.copy(self.cfg['instrument_parameters_path'], self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis/ref')
            except FileNotFoundError as error:
                self.logger.info(f'Failed to find instrument parameters with error {error}')
            
            for item in os.listdir():
                if self.cfg['file_name'] in item:
                    if 'analysis' not in item:
                        shutil.move(item, self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis/frames/' + item)
                        
            os.chdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            
            self.home_path = os.getcwd()
            shutil.move(self.original_path + '/error_output.txt', self.home_path + '/error_output.txt')
            
            os.chdir('frames')
            
            for run in os.listdir():
                if os.path.isdir(run):
                    os.chdir(run)
                    for files in os.listdir():
                        if files.endswith('master.h5'):
                            b = files.replace('_master.h5', '')
                            os.mkdir(self.home_path + '/analysis/' + b)
                            shutil.move(self.home_path + '/frames/' + run + '/' + files, self.home_path + '/frames/' + files)
                        elif files.endswith('.h5'):
                            shutil.move(self.home_path + '/frames/' + run + '/' + files, self.home_path + '/frames/' + files)
                    os.chdir('..')
                    shutil.rmtree(run)
                else:
                    if item.endswith('master.h5'):
                        b = item.replace('_master.h5', '')
                        os.mkdir(self.home_path + '/analysis/' + b)
                    elif files.endswith('.h5'):
                        shutil.move(self.home_path + '/frames/' + run + '/' + files, self.home_path + '/frames/' + files)
                            
            os.chdir(self.home_path + '/analysis')
            
            bkg_files = ['/GAIN.cbf', '/BKGINIT.cbf', '/BLANK.cbf', '/X-CORRECTIONS.cbf', '/Y-CORRECTIONS.cbf']
            for folder in os.listdir():
                os.symlink(self.home_path + '/frames', folder + '/img')
                for item in bkg_files:
                    shutil.copy(self.cfg['background_files_reference_path'] + item, self.home_path + '/ref' + item)
                    shutil.copy(self.home_path + '/ref' + item, folder)
                    
            os.chdir('..')
                    
        if self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis' not in self.home_path:
            os.chdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            self.home_path = os.getcwd()
            
        os.chdir(self.home_path + '/results/')
        tmp = os.listdir()
        tmp2 = []
        for item in tmp:
            tmp2.append(int(item))
        tmp2.sort()
        
        try:
            self.new_folder = int(tmp2[-1]) + 1
    
        except IndexError:
            self.new_folder = 1
            
        os.mkdir(self.home_path + '/results/' + str(self.new_folder))
        os.chdir(self.home_path)
        
        try:
            shutil.move(self.original_path + '/error_output.txt', self.home_path + '/error_output.txt')
        except FileNotFoundError:
            pass

    
    #This one is for VT - or dealing with any quick analysis from the synchrotron's autoprocessed data
    
    def Organise_Directory_Autoprocess(self):
        
        if not os.path.exists(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis') and not os.path.exists('analysis'): 
        
            os.mkdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            
            #User defines where they have their reference (assuming while at the synchrotron they did one up)
            #So before change all of the folders to make neat and tidy, first need to copy the reference from that location
            
            try:
                shutil.copy(self.cfg['reference_path'], self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            except FileNotFoundError as error:
                self.logger.info(f'Failed to find reference file with error {error}')
            
            for item in os.listdir():
                if self.cfg['file_name'] in item:
                    if 'analysis' not in item:
                        shutil.move(item, self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis/' + item)
                        
            os.chdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
            
            self.home_path = os.getcwd()
            shutil.move(self.original_path + '/error_output.txt', self.home_path + '/error_output.txt')
                
            tree_structure = ['analysis', 'ref', 'results', 'failed_autoprocessing']
            
            if not os.path.exists('analysis'):
                for item in tree_structure:
                    os.mkdir(item)
            
                for item in os.listdir():
                    if os.path.isdir(item) and item not in tree_structure:
                        shutil.move(item, self.home_path + '/analysis/' + item)
                    elif '.ins' in item:
                        shutil.move(item, self.home_path + '/ref/' + item)
                    
                os.chdir('analysis')
                
                #Code is unhappy when there are folders which failed the failed_autoprocessing
                
                #So this moves them to a different folder, which is also nice just to see :) 
                
                for run in os.listdir():
                    if os.path.isdir(run):
                        os.chdir(run)
                        if 'autoprocess.cif' not in os.listdir():
                            os.chdir('..')
                            shutil.move(self.home_path + '/analysis/' + run, self.home_path + '/failed_autoprocessing/' + run)
                        else:
                            os.chdir('..')
                
                #This next part adds numbers so folders are correctly ordered
                
                #Also allows for the fact that if the screenings auto-process they will be present too 
                        
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
                
            os.chdir(self.home_path)
            
        else:
            
            #This is just making sure the home_path and everything is CORRECT
            
            #Allows the user to start the code in either the main folder where ALL data sets are
            
            #OR they can start the code in the VT dataset that they are working with 
            
            if self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis' not in self.home_path:
                os.chdir(self.cfg['file_name'] + '_' + self.cfg['experiment_type'] + '_analysis')
                self.home_path = os.getcwd()
                



    
    
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        










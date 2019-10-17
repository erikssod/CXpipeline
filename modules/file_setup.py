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
        
        #This form is used where data reprocessing may be required (ie flexible mapping)
        
        #Will need to provide all frames and reference files into a single folder

        tree_structure = ['analysis', 'ref', 'input', 'results', 'frames']
        
        if not os.path.exists('analysis'):
            for item in tree_structure:
                os.mkdir(item)
            
            for files in os.listdir(self.home_path):
                if files.endswith('master.h5'):
                    b = files.replace('_master.h5', '')
                    os.mkdir('analysis/' + b)
            
            os.chdir('analysis')
            
            for folder in os.listdir():
                os.symlink(self.home_path + '/frames', folder + '/img')
                for bkg_file in self.cfg['XDS_background_files']:
                    if bkg_file in os.listdir(self.home_path):
                        shutil.copy(self.home_path + bkg_file, folder)
                
                
                #if self.cfg['experiment_type'] == 'flexible mapping':
                
                    #shutil.copy(self.home_path + '/GAIN.cbf', folder)
                    #shutil.copy(self.home_path + '/BKGINIT.cbf', folder)
                    #shutil.copy(self.home_path + '/BLANK.cbf', folder)
                    #shutil.copy(self.home_path + '/X-CORRECTIONS.cbf', folder)
                    #shutil.copy(self.home_path + '/Y-CORRECTIONS.cbf', folder)
                
            os.chdir('..')
            
            for files in os.listdir(self.home_path):
                if files.endswith(('.cbf', '.ins', '.XDS')):
                    shutil.move(self.home_path + '/' + files, self.home_path + '/ref/' + files)
                elif files.endswith('.INP'):
                    shutil.move(self.home_path + '/' + files, self.home_path + '/input/' + files)
                elif files.endswith('.h5'):
                    shutil.move(self.home_path + '/' + files, self.home_path + '/frames/' + files)
                    
        #Setting up folders to distinguish - this number goes up by 1 every time the entire code is run (to keep everything organised)
            
        os.chdir(self.home_path + '/results/')
        tmp = os.listdir()
        tmp2 = []
        for item in tmp:
            tmp2.append(int(item))
        tmp2.sort()

        try:
            new_folder = int(tmp2[-1]) + 1
            
        except IndexError:
            new_folder = 1    
                
        os.mkdir(self.home_path + '/results/' + str(new_folder))
        os.chdir(self.home_path)
        
        return new_folder
    
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


    
    
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        










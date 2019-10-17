#!/usr/bin/env python3

      
#----------Required Modules----------#

import os 
import pandas as pd
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import yaml
import logbook

#----------Function Definitions----------#

def VT_Analysis(df_cell_parameters, parameter_list):
    index = 0
    behaviour = []
    data = df_cell_parameters['_diffrn_ambient_temperature']
    
    #Searches through the data and classifies everything as a temperature minima, maxima, increasing or decreasing 
    
    #If the analysis doesn't work, this block where the behaviours are assigned is likely where it broke...
    
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
            elif i > data[index-1] and i == data[index+1]:
                behaviour.append('Increasing')
            elif i < data[index-1] and i == data[index+1]:
                behaviour.append('Decreasing')
            elif i == data[index-1]:
                behaviour.append('Did Not Change')
            else:
                behaviour.append('Error')
        
        #This else statement is needed to classify the first and last points 
        
        else:
            if index == 0:
                if i < data[index+1]:
                    behaviour.append('Increasing')
                elif i == data[index+1]:
                    behaviour.append('Did Not Change')
                else:
                    behaviour.append('Decreasing')
            else:
                if i < data[index-1]:
                    behaviour.append('Decreasing')
                elif i == data[index-1]:
                    behaviour.append('Did Not Change')
                else:
                    behaviour.append('Increasing')

        index += 1
    
    df_cell_parameters['behaviour'] = behaviour
    
    #Remove duplicates
    
    discrete_behaviour = list(dict.fromkeys(behaviour))
    
    separated_by_behaviour_dfs = []
    
    #Separates the dataframe by behaviour, then plots them all on the same graph so they have different colours depending on the behaviour of the temperature at that point 
    
    for item in discrete_behaviour:
        condition = df_cell_parameters['behaviour'] == item
        separated_by_behaviour_dfs.append(df_cell_parameters[condition])
        
    df_cell_parameters.to_csv('Unit_Cell_Parameters.csv', index = None)
        
    index = 0    
    
    for item in separated_by_behaviour_dfs:
        x = item[(i for i in parameter_list if 'temperature' in i)]
        y1 = item[(i for i in parameter_list if 'length_a' in i)]
        y2 = item[(i for i in parameter_list if 'length_b' in i)]
        y3 = item[(i for i in parameter_list if 'length_c' in i)]
        y4 = item[(i for i in parameter_list if 'alpha' in i)]
        y5 = item[(i for i in parameter_list if 'beta' in i)]
        y6 = item[(i for i in parameter_list if 'gamma' in i)]
        y7 = item[(i for i in parameter_list if 'volume' in i)]
        
        ax1 = plt.subplot(2, 4, 1)
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y1, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('a-axis')
        plt.legend()
        
        ax2 = plt.subplot(2, 4, 2)
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax2.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y2, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('b-axis')
        plt.legend()
        
        ax3 = plt.subplot(2, 4, 3)
        ax3.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax3.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y3, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel(r'Distance ($\AA$)')
        plt.title('c-axis')
        plt.legend()
        
        ax4 = plt.subplot(2, 4, 5)
        ax4.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax4.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y4, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('alpha')
        plt.legend()
        
        ax5 = plt.subplot(2, 4, 6)
        ax5.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax5.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y5, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('beta')
        plt.legend()
        
        ax6 = plt.subplot(2, 4, 7)
        ax6.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax6.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y6, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel('Angle('+chr(176)+')')
        plt.title('gamma')
        plt.legend()
        
        ax7 = plt.subplot(2, 4, 8)
        ax7.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax7.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y7, label = discrete_behaviour[index] + ' temperature')
        plt.xlabel('Temperature(K)')
        plt.ylabel(u'Volume (\u212B\u00B3)')
        plt.title('volume')
        plt.legend()
        
        index += 1
        
    figure = plt.gcf()
    figure.set_size_inches(16,12)
    plt.savefig('Variable_Temperature_Analysis.png', bbox_inches = 'tight', dpi = 100)
    plt.clf()

#----------Class Definitions----------#

class Cell_Parameter:  
    
    #The Cell_Parameter class is used to pull cell parameters from CIF files based on an input search term, and output them (with separated errors) into a dataframe

    def __init__(self, home_path):
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
        
        self.results = {}
        self.search_items = self.cfg['cell_parameters']
        self.cif_files = []
        self.errors = {}
        self.number_of_structures_in_cif = []
        self.df = pd.DataFrame() 
        
        for item in self.search_items:
            self.results[item] = []
            self.errors[item] = []
    
    def sorted_properly(self, data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)]
        
        return sorted(data, key=alphanum_key)
    
    def data(self):
        #Some problems if searching for parameters, and not all of them are found
        #Currently works if the only one found is the last parameter in the list
        #Found this out while working with the autoprocess.cif files 
        
        for dirName, subdirList, fileList in os.walk(os.getcwd()):
            sorted_fileList = self.sorted_properly(fileList)
            for files in sorted_fileList:
                if files.endswith('.cif') and files.lower() not in self.cif_files:
                    self.cif_files.append(files.lower())
                    self.logger.info(files)
                    with open(os.path.join(dirName, files), 'rt') as cif:
                        contents = cif.readlines()
                    for item in self.search_items:
                        temp4 = 0
                        results_tmp = []
                        errors_tmp = []
                                
                        self.logger.info('File ' + files + ' opened. Searching for parameter ' + item)
                                
                        for line in contents:
                            if item in line:
                                
                                self.logger.info('File ' + files + ' - found parameter ' + item)
                                
                                temp4 += 1    
                                if '(' in line:
                                    temp = line.strip(item).strip(' \n').split('(')
                                    temp3 = temp[1].strip(')')
                                    self.results[item].append(float(temp[0]))
                                    if '.' in line:
                                        temp2 = temp[0].split('.')
                                        self.errors[item].append(int(temp3)*10**-(int(len(temp2[1]))))
                                    else:
                                        self.errors[item].append(int(temp3))
                                else:
                                    temp = line.strip(item).strip(' \n')
                                    self.results[item].append(float(temp))
                                    self.errors[item].append(0)

                    self.number_of_structures_in_cif.append(temp4)
        
        for para in self.search_items:
            if len(self.results[para]) != 0:
                self.df[para] = self.results[para]
                self.df[para + '_error'] = self.errors[para]
                
        run_file = []
        cif_count = 1
        cif_count2 = 0

        for i in self.number_of_structures_in_cif:
            while cif_count <= i:
                run_file.append(self.cif_files[cif_count2])
                cif_count += 1
            cif_count2 += 1
            cif_count = 1

        self.df.insert(0, 'CIF Name', run_file)
        
        return self.df
  
    def __repr__(self):
        return "To obtain a dataframe with parameters {} from all CIF Files in the working dictionary and below, type object.data(). To change parameters, edit conf.yaml file".format(self.search_items) 
    
class VT_Analysis_Cell_Parameter(Cell_Parameter):
    
    #This is a subclass to do a VT_analysis for VT Data
    
    def process(self, df):
        try:
            VT_Analysis(df, self.search_items)
        except ValueError as error:
            self.logger.critical(f'Failed to process with error: {error}')
            exit()
        self.logger.info('Successfully processed data')

        
        
        
        



    




























    
    
    


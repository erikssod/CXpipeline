#!/usr/bin/env python3

####################################################################################
#-------------------------CX-ASAP: variable_temp_analysis--------------------------#
#---Authors: Amy J. Thompson, Kate M. Smith, Daniel J. Eriksson & Jason R. Price---#
#----------------------------Python Implementation by AJT--------------------------#
#-------------------------------Project Design by JRP------------------------------#
#-----------------------Valuable Coding Support by KMS & DJE-----------------------#
####################################################################################

#----------Instructions for Use----------#

#This module will analyse data from variable temperature experiments and provide graphs of cell changes

#Also applicable to any plot of changing cell dimensions, although temperature will be the x-axis

#Data file to be analysed should be specified in the config file and the script run from that same working directory 

#If run as a part of the pipeline, name of data file will be automatically populated 

#----------Required Modules----------#

import os 
import pandas as pd
import yaml
import logbook
import pathlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#----------Class Definition----------#

class VT_Analysis:  
    def __init__(self, location = 'temp', home_path = os.getcwd()):
        
        config = Config()
        
        self.cfg = config.cfg
        self.conf_path = config.conf_path
        self.logger = config.logger
                
        #if location == 'temp':
            #os.chdir(self.cfg['System_Parameters']['current_results_path'])
            
        os.chdir(location)
                
                
        #Set up empty lists and defines what the x/y axis headers are (assuming values from within this automation pipeline - user defined headers can be used later)
        
        self.behaviour = []
        self.vt_headers_y = ["_cell_length_a", "_cell_length_b", "_cell_length_c", "_cell_angle_alpha", "_cell_angle_beta", "_cell_angle_gamma", "_cell_volume"]
        for item in self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['cell_parameters']:
            
            #allows for variation in which CIF temperature parameter is used 
            
            if 'temperature' in item:
                self.vt_headers_x = item
                continue 
    
    def import_data(self, data):
        
        #Simply a function to import data , with the file name for data specified 
        
        self.df = pd.read_csv(data)
        
    def graph(self, x, y, title, subplot, behaviour):
        
        #This is to avoid writing out the script for the graphs 7 times 
        
        ax = plt.subplot(2, 4, subplot)
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(10))
        plt.scatter(x, y, label = behaviour)
        plt.xlabel('Temperature(K)')
        if 'alpha' or 'beta' or 'gamma' in title.lower():
            plt.ylabel('Angle('+chr(176)+')')
        elif 'vol' in title.lower():
            plt.ylabel(u'Volume (\u212B\u00B3)')
        else:
            plt.ylabel(r'Distance ($\AA$)')
        plt.title(title)
        plt.legend()
        
    def graph_full(self, x, y, x_title, y_title, y_series_title, graph_title, colour = None, marker = None, linewidth = None, s = None):
        
        #Function to plot the graphs to condense the code a bit with optional changes to the aesthetics of the plot 
        
        for index, item in enumerate(y):
            if colour == None:
                plt.scatter(x, item, label = y_series_title[index])
            else:
                plt.scatter(x, item, c = colour[index], marker = marker[index], linewidth = linewidth[index], s = s[index], label = y_series_title[index])
        plt.xlabel(x_title, fontsize = 12)
        plt.ylabel(y_title, fontsize = 12)
        plt.title(graph_title)
        plt.legend(fontsize = 12)
        
    def determine_temp_behaviour(self):
        
        #Searches for the temperature parameter used 
        
        if self.cfg['Extra_User_Parameters_Individual_Modules']['use_custom_headings'].lower() == 'no':
        
            for item in self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['cell_parameters']:
                if 'temperature' in item and 'error' not in item:
                    self.temperature_parameter = item
                    
        else:
             self.temperature_parameter = self.cfg['Extra_User_Parameters_Individual_Modules']['user_headings_x']
        
        data = self.df[self.temperature_parameter]
        
        #Searches through the data and classifies everything as a temperature minima, maxima, increasing or decreasing 
    
        for index, i in enumerate(data):
            if index != 0 and index != len(data) - 1:
                if i < data[index-1] and i < data[index+1]:
                    self.behaviour.append('Minima')
                elif i > data[index-1] and i > data[index+1]:
                    self.behaviour.append('Maxima')
                elif i < data[index-1] and i > data[index+1]:
                    self.behaviour.append('Decreasing')
                elif i > data[index-1] and i < data[index+1]:
                    self.behaviour.append('Increasing')
                elif i > data[index-1] and i == data[index+1]:
                    self.behaviour.append('Increasing')
                elif i < data[index-1] and i == data[index+1]:
                    self.behaviour.append('Decreasing')
                elif i == data[index-1]:
                    self.behaviour.append('Did Not Change')
                else:
                    self.behaviour.append('Error')
            
            #This else statement is needed to classify the first and last points 
            
            else:
                if index == 0:
                    if i < data[index+1]:
                        self.behaviour.append('Increasing')
                    elif i == data[index+1]:
                        self.behaviour.append('Did Not Change')
                    else:
                        self.behaviour.append('Decreasing')
                else:
                    if i < data[index-1]:
                        self.behaviour.append('Decreasing')
                    elif i == data[index-1]:
                        self.behaviour.append('Did Not Change')
                    else:
                        self.behaviour.append('Increasing')
                        
        self.df['behaviour'] = self.behaviour 
        
        return self.behaviour
      
    def analysis(self):
       
       #Remove duplicates to define search condition to separate dataframes by their behaviour - this allows for the output graphs to be colour-coded 
    
        self.discrete_behaviour = list(dict.fromkeys(self.determine_temp_behaviour()))
        
        separated_by_behaviour_dfs = []
        
        for item in self.discrete_behaviour:
            condition = self.df['behaviour'] == item
            separated_by_behaviour_dfs.append(self.df[condition])
        
        for index, item in enumerate(separated_by_behaviour_dfs):
            if self.cfg['Extra_User_Parameters_Individual_Modules']['use_custom_headings'].lower() == 'no':
                x = item[self.vt_headers_x]
                counter = 1
                for param in self.vt_headers_y:
                    y = item[param] 
                    self.graph(x,y,param,counter, self.discrete_behaviour[index] + ' temperature')
                    counter += 1
            else:
                x = item[self.cfg['Extra_User_Parameters_Individual_Modules']['user_headings_x']]
                counter = 1
                for param in self.cfg['Extra_User_Parameters_Individual_Modules']['user_headings_y']:
                    y = item[param]
                    self.graph(x,y,param,counter, self.discrete_behaviour[index] + ' temperature')
                    counter += 1        
                    
                    
        figure = plt.gcf()
        figure.set_size_inches(16,12)
        plt.savefig('Variable_Temperature_Analysis.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()
        
        #Plot Statistics
        
        self.graph_full(self.df['_diffrn_ambient_temperature'], [self.df['_diffrn_reflns_av_R_equivalents'], self.df['_diffrn_measured_fraction_theta_full'], self.df['_refine_ls_R_factor_gt']],'Temperature(K)', 'Statistic', ['Rint', 'Completeness', 'R-Factor'], 'Overall Data Statistics')
        
        figure = plt.gcf()
        figure.set_size_inches(16,12)
        plt.savefig('Variable_Temperature_Statistics.png', bbox_inches = 'tight', dpi = 100)
        plt.clf()
                   
#If the module is run independently, the class is initialised, and the analysis is run 
  
if __name__ == "__main__":
    from system.yaml_configuration import Nice_YAML_Dumper, Config
    vt_analysis = VT_Analysis(os.getcwd())
    vt_analysis.import_data(vt_analysis.cfg['Extra_User_Parameters_Individual_Modules']['data_file_name'])
    vt_analysis.analysis()
else:
    from .system.yaml_configuration import Nice_YAML_Dumper, Config

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
    
    def import_data(self, data, bonds=None, angles = None, torsions = None):
        
        #Simply a function to import data , with the file name for data specified 
        
        self.df = pd.read_csv(data)
        if bonds != None:
            self.df_bonds = pd.read_csv(bonds)
        else:
            self.df_bonds = pd.DataFrame()
        if angles != None:
            self.df_angles = pd.read_csv(angles)
        else:
            self.df_angles = pd.DataFrame()
        if torsions != None:
            self.df_torsions = pd.read_csv(torsions)
        else:
            self.df_torsions = pd.DataFrame()
        
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
      
    def structural_analysis(self, df, components, structure_type, file_name, folder_name, y_unit):
        if df.empty == False:
            structure_list = []
            reverse_structure_list = []
            important_structures = pd.DataFrame()
            important_structures_list = []
            reverse_important_structures_list = []
            headings = list(df)
            
            for index, item in enumerate(df[headings[0]]):
                string = ''
                reverse_string = ''
                for column in headings:
                    if column in components[0:-1]:
                        string += ('-' + str(df[column][index]))
                        
                intermediate = string.strip('-').split('-')
                
                for i in range(len(intermediate) -1, -1, -1):
                    reverse_string += (intermediate[i] + '-')
                    
                structure_list.append(string.strip('-'))
                reverse_structure_list.append(reverse_string.strip('-'))
            
            df[structure_type] = structure_list
            df['Reverse_' + structure_type] = reverse_structure_list
            
            cif_list = self.df['CIF File'].values.tolist()
            temperature_list = self.df['_diffrn_ambient_temperature'].values.tolist()
            new_temp_list = []
            for i, item in enumerate(cif_list):
                for j, value in enumerate(df['Cif File']):
                    if item == value:
                        new_temp_list.append(temperature_list[i])

            df['Temperature'] = new_temp_list
            df.to_csv(file_name, index = None)
            discrete_structures = list(dict.fromkeys(df[structure_type]))
            reverse_discrete_structures = list(dict.fromkeys(df['Reverse_' + structure_type]))
            separated_by_structure_dfs = []
            important_separated_by_structure_dfs = []
            
            for index, item in enumerate(discrete_structures):
                condition = df[structure_type] == item
                condition2 = df['Reverse_' + structure_type] == item
                df_double = [df[condition], df[condition2]]
                separated_by_structure_dfs.append(pd.concat(df_double))
                
            try:
                os.mkdir(folder_name)
            except FileExistsError:
                pass
                
            for index, item in enumerate(separated_by_structure_dfs):
                del item['Reverse_' + structure_type]
                list_for_structure_names = list(item[structure_type])
                os.chdir(folder_name)
                item.to_csv(structure_type + '_' + list_for_structure_names[0] + '.csv', index = None)
                os.chdir('..')
        
            for item in discrete_structures:
                for atom in self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['atom_for_bond_analysis']:
                    if atom in item:
                        important_structures_list.append(item)
                        
            for item in reverse_discrete_structures:
                for atom in self.cfg['User_Parameters_Full_Pipeline']['Analysis_Requirements']['atom_for_bond_analysis']:
                    if atom in item:
                        reverse_important_structures_list.append(item)
            
            for index, item in enumerate(important_structures_list):
                condition = df[structure_type] == item
                condition2 = df['Reverse_' + structure_type] == item
                df_double = [df[condition], df[condition2]]
                important_separated_by_structure_dfs.append(pd.concat(df_double))
             
            y_data = []
            y_headers = []
            
            for index, item in enumerate(important_separated_by_structure_dfs):
                del item['Reverse_' + structure_type]
                
                #x_data = temps_for_structure
                x_data = item['Temperature']
                y_data.append(item[components[-1]])
                y_headers.append(important_structures_list[index])
        
            self.graph_full(x_data, y_data, 'Temperature (K)', y_unit, y_headers, structure_type)
            figure = plt.gcf()
            figure.set_size_inches(16,12)
            plt.savefig(structure_type + '.png', bbox_inches = 'tight', dpi = 100)
            plt.clf()
                
            important_structures = pd.concat(important_separated_by_structure_dfs)
            important_structures.to_csv('Important_' + file_name, index = None)
                      
            
    
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
        

        #Investigate bond-length changes
        
        bond_paras = ['_geom_bond_atom_site_label_1', '_geom_bond_atom_site_label_2', '_geom_bond_distance']
        angle_paras = ['_geom_angle_atom_site_label_1', '_geom_angle_atom_site_label_2', '_geom_angle_atom_site_label_3', '_geom_angle']
        torsion_paras = ['_geom_torsion_atom_site_label_1', '_geom_torsion_atom_site_label_2', '_geom_torsion_atom_site_label_3', '_geom_torsion_atom_site_label_4', '_geom_torsion']
        
        
        self.structural_analysis(self.df_bonds, bond_paras, 'Bonds', 'Bond_Lengths.csv', 'Individual_Bond_Length_Data', 'Length (Angstroms)')
        self.structural_analysis(self.df_angles, angle_paras, 'Angles', 'Bond_Angles.csv', 'Individual_Angle_Data', 'Angle (Degrees)')
        self.structural_analysis(self.df_torsions, torsion_paras, 'Torsions', 'Bond_Torsions.csv', 'Individual_Torsion_Data', 'Angle (Degrees)')
        
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
    vt_analysis.import_data(vt_analysis.cfg['Extra_User_Parameters_Individual_Modules']['data_file_name'], vt_analysis.cfg['Extra_User_Parameters_Individual_Modules']['data_file_name_bonds'], vt_analysis.cfg['Extra_User_Parameters_Individual_Modules']['data_file_name_angles'], vt_analysis.cfg['Extra_User_Parameters_Individual_Modules']['data_file_name_torsions'])
    vt_analysis.analysis()
else:
    from .system.yaml_configuration import Nice_YAML_Dumper, Config

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:31:40 2021

@author: Nassim
"""

import matplotlib.pyplot as plt
import numpy as np
import xlsxwriter
import os


class Excel:
    
    def __init__(self, folder, path):
        
        self.folder = folder
        self.path = path
        output_name = f"{self.folder}_results.xlsx"
        output_path = os.path.join(self.path, output_name)
        self.workbook = xlsxwriter.Workbook(f"{output_path}")
        self.bold = self.workbook.add_format({"bold": True})
        self.red = self.workbook.add_format({"font_color": "red"})
        self.sheet = self.workbook.add_worksheet("Surface area")
        self.sheet_2 = self.workbook.add_worksheet("Slope")
        
        
    def write_excel(self, data, slope_data, slope_data_1, excel_index, name, 
                    time):
        """
        Function that writes all data in an excel file 
        which will be stored in the same 
        directory as the main_folder from main.py.
        """
        
        bold = self.workbook.add_format({'bold': True})
        
        self.sheet.write(excel_index, 0, 'Time [hours]', bold)
        self.sheet.write(excel_index+1, 0, f'Folder {name} [micrometer^2]', bold)
        
        
        for i in range(len(data)):
            
            if data[i] == 0:
                self.sheet.write(excel_index+1, i+1, data[i], self.red)
            else:
                self.sheet.write(excel_index+1, i+1, data[i])
            self.sheet.write(excel_index, i+1, np.around(time[i], decimals=1))
            
        self.sheet_2.write(0, 0, 'Files', bold)
        self.sheet_2.write(0, 1, 'Exponential slope [a for a*exp(x)]', bold)
        self.sheet_2.write(excel_index+1, 0, f'{name}', bold)
        self.sheet_2.write(excel_index+1, 1, slope_data)
        
        self.sheet_2.write(0, 2, 'Linear slope [micrometer^2/hour]', bold)
        self.sheet_2.write(excel_index+1, 2, slope_data_1)
        
            
    def close(self):
        self.workbook.close()
        
        
def analyse(result, x_result, name, path, excel, excel_index):
    """
    Initialisation function for the analysis of given data
    """
    
    
    def exp_fit(x, a, b):
        return [a*np.exp(x[i]*b) for i in range(len(x))]
    
    def lin_fit(x, a, b):
        return [a*t+b for t in x]
    

    from scipy.optimize import curve_fit
    popt, __ = curve_fit(exp_fit, x_result, result, p0=[553, 0])
    slope = np.around(popt[0], decimals=0)
    start = np.around(popt[1], decimals=2)
    fit = exp_fit(x_result, popt[0], popt[1])
    
    popt_1, __ = curve_fit(lin_fit, x_result, result, p0=[0, 0])
    fit_1 = lin_fit(x_result, popt_1[0], popt_1[1])
    slope_1 = np.around(popt_1[0], decimals=0)

     
    if len(result) < 10:
        
        plot(name, path,
             Measured=[x_result, result],
             Exponential_fit=[x_result, fit],
             Linear_fit=[x_result, fit_1])
        
    else:
        weight = 10
        sma = simple_moving_average(result, weight)
        x_sma = x_result[0:1-weight]
        valleys, peaks = peaks_and_valleys(x_sma, sma)
        collapses, rises = peak_valley_change(valleys[0], 
                                              valleys[1], 
                                              peaks[0], 
                                              peaks[1])
   
        plot(name, path,
             Measured=[x_result, result],
             Valleys=valleys,
             Peaks=peaks, 
             SMA=[x_sma, sma],
             Exponential_fit=[x_result, fit],
             Linear_fit=[x_result, fit_1])

    excel.write_excel(result, slope, slope_1, excel_index, name, x_result)   
                      
    

def simple_moving_average(values, window):      #valley and peak detection
    """
    Calculates the simple moving average of data within a certain window.
    """
    weight = np.repeat(1/(window), window)
    simple_moving_av = np.convolve(values, weight, 'valid')
    
    return simple_moving_av


def peaks_and_valleys(x, y):                #peak and valley detection            
    """
    Given initial data this function will search for peaks and valleys
    threshold value determines the amount of data points between two significant
    peaks or valleys.
    
    Impr --> Measure how long a rise or fall lasts to define peaks and valleys.
    """        
    x_dal_waarden = [0]                      #Lokal lists and variables
    dal_waarden = [0]
    top_waarden = [0]
    x_top_waarden = [0]
    x_dal = 0
    x_top = 0
    dal = 0
    top = 0
    threshold = 2        #Assuming there are no significant peaks and valleys within threshold value of each other
    
    for i in range(len(y)-2):
        if y[i+1] >= y[i] and y[i+1] >= y[i+2]:
            top = y[i+1]
            x_top = x[i+1]
            for r in range(i, len(y)-2):
                if y[r] >= top and (x[r]-threshold) > x_top:
                    top = y[r]
                    x_top = x[r]
                    x_top_waarden.append(x_top)
                    top_waarden.append(top)
                    break
            
        elif y[i+1] <= y[i] and y[i+1] <= y[i+2] and dal_waarden[-1] <= y[i+1]: #define valleys and make sure that they are properly spaced
            dal = y[i+1]
            x_dal = x[i+1]
            for r in range(i, len(y)-2):
                if y[r] <= dal and (x[r]-threshold) > x_dal: 
                    dal = y[r]
                    x_dal = x[r]
                    x_dal_waarden.append(x_dal)
                    dal_waarden.append(dal)
                    break
            
    return [x_dal_waarden, dal_waarden], [x_top_waarden, top_waarden]
        

def peak_valley_change(x_valleys, y_valleys, x_peaks, y_peaks):
    """
    Function that returns the collapses and rises of peak and valley input data,
    by looking for consecutive peaks and valleys or valleys and peaks respectively.
    """
    collapses = []
    rises = []

    
    for i in range(1, len(y_peaks)-1):
        for r in range(1, len(y_valleys)):
            if (x_peaks[i+1]-x_peaks[i]) > (x_peaks[i]-x_valleys[r]):
                down_percentage = round((y_valleys[r]-y_peaks[i])/
                                        y_peaks[i]*100, 3)
                collapses.append(f'{x_peaks[i]}, {down_percentage}')
                break
            
    for i in range(1, len(y_valleys)-1):
        for r in range(1, len(y_peaks)):
            if (x_valleys[i+1]-x_valleys[i]) > x_valleys[i]-x_peaks[r]:
                up_percentage = round((y_peaks[r]-y_valleys[i])/
                                      y_peaks[r]*100, 3)
                rises.append(f'{x_valleys[i]}, {up_percentage}')
                break
    return collapses, rises


def plot(name, path, **kwargs):
    """
    Function that plots all given data, only that the data is inserted as:
    data=[x_data, y_data].
    Colors and linetypes can be adjusted by adjusting the colors and lintypes
    lists.
    """
    #order=Measured, Valleys, Peaks, SMA, Fit
    colors = ['g', 'r', 'y', 'b', 'c', 'm', 'k', 'w']
    lintypes = ['-', 'o', 'o', '-', '--', '--']
    i = 0
    for result, data in kwargs.items():
        plt.plot(data[0], data[1], lintypes[i], color=colors[i], label=str(result))
        plt.xlim(left=data[0][0])
        i += 1
        
    
    plt.title('Surface area of blastocyt in the '+ name +' folder')
    plt.xlabel('Time [h]')
    plt.ylabel('Surface area [mu^2 meter]')
    plt.legend()
    plt.grid()
    
    
    import os
    plot_directory = 'plots'
    plot_dir_path = os.path.join(path, plot_directory)
    os.makedirs(plot_dir_path, exist_ok=True)
    fig_name = f'figure_{name}'
    save_path = os.path.join(plot_dir_path, fig_name)
    plt.savefig(save_path)
    plt.close()
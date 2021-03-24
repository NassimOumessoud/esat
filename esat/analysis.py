# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:31:40 2021

@author: Nassim
"""

import matplotlib.pyplot as plt
import numpy as np

          
def analyse(result, workbook, sheet, sheet_2, exc_index, name, weight, x_result,
            path):
    """
    Initialisation function for the analysis of given data
    """
    
    sma = simple_moving_average(result, weight)
    x_sma = x_result[0:1-weight]
    valleys, peaks = peaks_and_valleys(x_sma, sma)
    collapses, rises = peak_valley_change(valleys[0], 
                                          valleys[1], 
                                          peaks[0], 
                                          peaks[1])
    def fit(x, a, b):
        return [a*np.exp(x[i]*b) for i in range(len(x))]
    
    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(fit, x_result, result, p0=[553, 0])
    slope = np.around(len(result)/(x_result[-1]-x_result[0])*popt[0], decimals=0)
    start = np.around(popt[1], decimals=2)
    lin_fit = fit(x_result, popt[0], popt[1])
    
    plot(result, sma, x_sma, valleys, peaks, collapses, lin_fit, rises, x_result,
                                                              name, path)
    to_excel(result, slope, start, workbook, sheet, sheet_2, exc_index, name,
             collapses, rises, x_result)    


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
                down_percentage = (y_valleys[r]-y_peaks[i])/y_peaks[i]*100
                collapses.append(f'{x_peaks[i]}, {down_percentage}')
                break
            
    for i in range(1, len(y_valleys)-1):
        for r in range(1, len(y_peaks)):
            if (x_valleys[i+1]-x_valleys[i]) > x_valleys[i]-x_peaks[r]:
                up_percentage = (y_peaks[r]-y_valleys[i])/y_peaks[r]*100
                rises.append(f'{x_valleys[i]}, {up_percentage}')
                break
    return collapses, rises


def plot(data, trend, x_trend, data_1, data_2, data_3, data_4, data_5, x_data, 
         name, path):
    """
    Function that plots all data
    """
    colors = ['g', 'r', 'y', 'b', 'c', 'm', 'k', 'w']
    
    plt.plot(x_data, data, '-', color = 'k', label='Measured')
    plt.plot(x_trend, trend, '.-', lw=4, color = 'g', label = 'Simple moving average')
    plt.xlabel('Time [h]')
    plt.ylabel('Surface area [mu meter]')
    plt.title('plot')
    plt.title('Surface area of blastocyt in the '+ name +' folder')
    plt.plot(data_1[0], data_1[1], 'o', color='r', label='Valley')
    plt.plot(data_2[0], data_2[1], 'o', color = 'm', label='Peak')
    plt.plot(x_data, data_4, '--', lw=2, color='r', label='linear fit')
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
    
    
def to_excel(data, slope_data, start_data, workbook, sheet, sheet_2, exc_index, name,
             collapses, rises, time):
    """
    Function that writes all data in an excel file which will be stored in the same 
    directory as the main_folder from main.py.
    """
    bold = workbook.add_format({'bold': True})
    
    sheet.write(exc_index, 0, 'Time [hours]', bold)
    sheet.write(exc_index+1, 0, f'Folder {name} [micrometer^2]', bold)
    for i in range(len(data)):
        sheet.write(exc_index+1, i+1, data[i])
        sheet.write(exc_index, i+1, np.around(time[i], decimals=1))
        
    sheet_2.write(0, 0, 'Files', bold)
    sheet_2.write(0, 1, 'Slope [micrometer^2/hour]', bold)
    sheet_2.write(exc_index+1, 0, f'{name}', bold)
    sheet_2.write(exc_index+1, 1, slope_data)
    sheet_2.write(exc_index+1, 2, start_data)
    for i, collaps in enumerate(collapses):
        sheet_2.write(exc_index+2, 0, 'Collapses ->')
        sheet_2.write(exc_index+2, i+1, collaps)
    
        
    
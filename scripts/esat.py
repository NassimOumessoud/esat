# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 10:56:48 2020

@author: Nassim
"""
import os

import cv2
import numpy as np


def run(main_folder, t_start, t_end, weight=10, growth=2, shrink=2):
    """
    Main function that controls the circle analysis and passes the resluts to
    the analysis file.
    """
    import time

    t1 = time.time()
    directory = f"{main_folder}_analysed"
    path = os.path.join(main_folder, directory)
    os.makedirs(path, exist_ok=True)
    output_name = f"{main_folder}_results.xlsx"
    output_path = os.path.join(path, output_name)
    

    import xlsxwriter

    export = xlsxwriter.Workbook(f"{output_path}")
    bold = export.add_format({"bold": True})
    red = export.add_format({"font_color": "red"})
    export_sheet = export.add_worksheet("Surface area")
    export_sheet_2 = export.add_worksheet("Slope")
    

    import imp

    import analysis

    imp.reload(analysis)
    print("reloaded analysis")
    

        
    column = 0
    for i, sub_folder in enumerate(os.listdir(main_folder)):  # open main folder
        
        if os.path.isdir(sub_folder):
            print('Sub_folder is a folder')
            img_folder = f"Circles_{sub_folder}"
            img_path = os.path.join(path, img_folder)
            os.makedirs(img_path, exist_ok=True)
            route = os.path.join(main_folder, sub_folder)
            
            
        elif os.path.isfile(sub_folder):
            print('Sub_folder is a file')
            img_folder = f"Circles_{main_folder}"
            img_path = os.path.join(path, img_folder)
            os.makedirs(img_path, exist_ok=True)
            route = os.path.join(main_folder, sub_folder)
def process()
            results = files(route, img_path)
            print('I got results!')  
            x = [
                    round(e, 1)
                    for e in np.linspace(t_start[i], t_end[i], len(results))
                    ]

#        export_sheet.write(column + 2, 0, "Removed data points [hour]", bold)
        #        for ind, e in enumerate(removed):
        #            export_sheet.write(column+2, ind+1, np.around(x[e-1], decimals=1), red)

            analysis.analyse(
                results,
                export,
                export_sheet,
                export_sheet_2,
                column,
                sub_folder,
                weight,
                x,
                path,
            )
            column += 4
            export.close()
            t2 = time.time()
            dt = t2 - t1
            print("Deze analyse duurde totaal %.3f minuten" % (dt / 60))


def files(route, img_path):
    """
    Function that searches for all the files inside the folder route, then passes
    the files to the circle detector and retrieves the radius of the
    """
    surfaces = []
    for dirpath, _, files in os.walk(route):  # open een van de 7 folders
        file_counter = 0
        radius = 0
        for file_name in files:  # Zoek fotos per folder
            file_path = os.path.join(dirpath, file_name)  # Voeg path en file_name samen
            mid = len(files) / 2
            image = cv2.imread(file_path, 0)  # Lees image via path in zwart\wit
            min_rad = int(round(radius * 0.8))
            min_rad = 200
            max_rad = 500
            result = detect_circle(image, min_rad, max_rad)
            if result:
                radius, center, surface, img = result
                surfaces.append(surface)
                
                img_file = os.path.join(img_path, str(file_counter))
                cv2.imwrite(img_file + ".png", img)
                cv2.waitKey(0)
                
    return surfaces


def detect_circle(img, min_radius, max_radius, p1=200, p2=100):
    """
    Detects circles with a given min and max radius in an image. Param1 and param2
    refer to the canny edge detection that the HoughCircles uses to detect the
    circles.
    """
 
    for p in range(p1, p2, -10):

        detected_circles = cv2.HoughCircles(
            img,
            cv2.HOUGH_GRADIENT,
            1.5,
            290,
            param1=p,
            param2=p / 2,
            minRadius=min_radius,
            maxRadius=max_radius)
        

        if detected_circles is not None:
            detected_circles_rounded = np.uint16(np.around(detected_circles))
            for i in detected_circles_rounded[0, :]:
                    cv2.circle(img, (i[0], i[1]), i[2], (255), 5)  # Teken cirkel
                    radius = pixels_to_micrometers(i[2], img)
                    area = round(circular_area(radius))
                    return radius, (i[0], i[1]), area, img
        else:
            continue


def pixels_to_micrometers(pixels, image):
    """
    Converts pixels to micrometers with a resolution of 3 pixels/micrometer
    """
    if len(image) == 800:
        c = 3
    else:
        c = 1.6
    return pixels / c  # aantal micrometer


def circular_area(radius):
    """
    Uses the radius of a circle to determine its surface area
    """
    return np.pi * (radius ** 2)

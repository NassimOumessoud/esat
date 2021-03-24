# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 10:56:48 2020

@author: Nassim
"""
import cv2
import numpy as np
import os


def run(main_folder, tstart, teind, weight=10, growth=2, shrink=2):
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
    column = 0

    import analysis
    import imp

    imp.reload(analysis)
    print("reloaded analysis")

    for i, sub_folder in enumerate(os.listdir(main_folder)):  # open main folder
        img_folder = f"Circles_{sub_folder}"
        img_path = os.path.join(path, img_folder)
        os.makedirs(img_path, exist_ok=True)
        route = os.path.join(main_folder, sub_folder)
        results = files(route, img_path)

        _, stepsize = np.linspace(tstart[i], teind[i], len(results), retstep=True)
        x = [
            e - stepsize
            for e in np.linspace(tstart[i], teind[i] + stepsize, len(results))
        ]
        if x[0] != tstart[i]:
            x = [
                e - 2 * stepsize
                for e in np.linspace(tstart[i], teind[i] + 2 * stepsize, len(results))
            ]
        #        print(results + 'pre-clean')
        #        results, x_results, removed = cleaner(results, x , growth, shrink)
        #        print(results + 'post-clean')
        export_sheet.write(column + 2, 0, "Removed data points [hour]", bold)
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
    for dirpath, _, files in os.walk(route):  # open een van de 7 folders
        file_counter = 0
        surfaces = []
        r = 0
        for file_name in files:  # Zoek fotos per folder
            file_path = os.path.join(dirpath, file_name)  # Voeg path en file_name samen
            mid = len(files) / 2
            image = cv2.imread(file_path, 0)  # Lees image via path in zwart\wit
            min_rad = int(round(r * 0.8))
            if file_counter <= mid:
                file_counter += 1
                max_rad = 120  # telt het aantal fotos
            else:
                file_counter += 1
                max_rad = 180

            r, center, s, img = detect_circle(image, min_rad, max_rad)
            surfaces.append(s)
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
        detect_circles = cv2.HoughCircles(
            img,
            cv2.HOUGH_GRADIENT,
            1.5,
            290,
            param1=p,
            param2=p / 2,
            minRadius=min_radius,
            maxRadius=max_radius,
        )
        if detect_circles is not None:
            detect_circles_rounded = np.uint16(np.around(detect_circles))
            for i in detect_circles_rounded[0, :]:
                if (100 <= i[0] <= 400) & (100 <= i[1] <= 400):
                    cv2.circle(img, (i[0], i[1]), i[2], (255), 5)  # Teken cirkel
                    rad = convert_pixels_to_micrometers(i[2])
                    ar = round(area(rad))
                    return rad, (i[0], i[1]), ar, img
        else:
            continue


def convert_pixels_to_micrometers(pixels):
    """
    Converts pixels to micrometers with a resolution of 3 pixels/micrometer
    """
    return pixels / 3  # aantal micrometer


def area(radius):
    """
    Uses the radius of a circle to determine its surface area
    """
    return np.pi * (radius ** 2)

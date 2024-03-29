import os
import cv2
import numpy as np
import analysis


def pixels_to_micrometers(pixels, image):
    """
    Converts pixels to micrometers with a resolution of 3 pixels/micrometer
    """
    if image == 800:
        c = 3
        well_size = 333
        
    else:
        c = 1.6
        well_size = 177
    micrometers = pixels/c
    
    return micrometers, well_size


def circular_area(radius):
    """
    Uses the radius of a circle to determine its surface area
    """
    return np.pi * (radius ** 2)


def run(main_folder, times, growth=20, shrink=20):
    """
    Main function that controls the circle analysis and passes the resluts to
    the analysis file.
    """
    import imp
    imp.reload(analysis)
    print("reloaded analysis")
    import time

    t1 = time.time()
    output_directory = f"{main_folder}_analysed"
    path = os.path.join(main_folder, output_directory + '/')
    os.makedirs(path, exist_ok=True)
        
    excel = analysis.Excel(main_folder, path)
    column = 0
    
    for i, item in enumerate(os.listdir(main_folder)):
        
        item_path = os.path.join(main_folder, item)
        
        if os.path.isdir(item_path):
            
            img_folder = f"Circles_{item}"
            outliers_folder = f"Faulty_circles_{item}"
            
            img_path = (os.path.join(path, img_folder), 
                        os.path.join(path, outliers_folder))
            
            os.makedirs(img_path[0], exist_ok=True)
            os.makedirs(img_path[1], exist_ok=True)
            
            route = item_path     #route for a folder
            process(route, img_path, path, times, 
                    item, excel, i=i, col=column, growth=growth, shrink=shrink)
            column += 4
            
        elif os.path.isfile(item_path):
            img_folder = f"Circles_{main_folder}"
            img_path = os.path.join(path, img_folder)
            os.makedirs(img_path, exist_ok=True)
            route = main_folder                        
            process(route, img_path, path, times, main_folder, excel)
            break
        
        
    excel.close()
    t2 = time.time()
    dt = t2 - t1
    print("Deze analyse duurde totaal %.3f minuten" % (dt / 60))


def process(route, img_path, output_path, times, folder, excel, shrink=20,
            growth=20, i=0, col=0):
    
            results = files(route, img_path, shrink, growth)
            t_start, t_end = times
            
#            try: 
#                x = [
#                 np.around(e, decimals=1)
#                 for e in np.arange(t_start[i], t_end[i], 9.5/60)
#                 ] 
#                
#                analysis.analyse(results, x, folder, output_path, excel, col)
#            
#            except ValueError:
            x = [
                 np.around(e, decimals=1)
                 for e in np.linspace(t_start[i], t_end[i], len(results))
                 ] 
        
            analysis.analyse(results, x, folder, output_path, excel, col)
            

def files(route, img_path, shrink, growth):
    """
    Function that searches for all the files inside the folder route, then passes
    the files to the circle detector and retrieves the radius of the
    """
    surfaces = []
    outliers = []
    images, outlying_images = img_path

    for dirpath, _, files in os.walk(route):
        file_counter = 0
        radius = 100     #First guess
        well = 177
        files.sort()
        
        for file_name in files:
            file_path = os.path.join(dirpath, file_name)
            image = cv2.imread(file_path, 0)  
            
            min_rad = int(round(radius * (1-shrink*0.01)))
            max_rad = int(round(radius * (1+growth*0.01)))
                
            result = detect_circle(image, min_rad, max_rad)
            
            
            if result:
                radius, center, img = result
                
                if radius >= well:
               
                    mm_radius, well = pixels_to_micrometers(radius, len(img))
                    area = round(circular_area(mm_radius))
                    outliers.append(area)
                    surfaces.append(0)
                    
                    radius = 100
                    img_file = os.path.join(outlying_images, file_name)
                    cv2.imwrite(img_file + ".png", img)
                    cv2.waitKey(0)
                    
                    
                elif radius < well:
                    mm_radius, well = pixels_to_micrometers(radius, len(img))
                    area = round(circular_area(mm_radius))
                    
                    if area <= 9000: #small radii probably incorrect
                        area = 0
                        
                    surfaces.append(area)
                    
                    img_file = os.path.join(images, file_name)
                    cv2.imwrite(img_file + ".png", img)
                    cv2.waitKey(0)
                    file_counter += 1
                
    return surfaces


def detect_circle(img, min_radius, max_radius, p1=160, p2=100):
    """
    Detects circles with a given min and max radius in an image. Param1 and param2
    refer to the canny edge detection that the HoughCircles uses to detect the
    circles.
    """
    
    img_blur = cv2.medianBlur(img, 7)
    for p in range(p1, p2, -10):

        detected_circles = cv2.HoughCircles(
            img_blur,
            cv2.HOUGH_GRADIENT,
            1.5,
            290,
            param1=p,
            param2=p / 4,
            minRadius=min_radius,
            maxRadius=max_radius)
        

        if detected_circles is not None:
            detected_circles_rounded = np.uint16(np.around(detected_circles))
            for i in detected_circles_rounded[0, :]:
                    cv2.circle(img, (i[0], i[1]), i[2], (255), 5)  # Teken cirkel
                    radius = i[2]
                    return radius, (i[0], i[1]), img
        else:
            continue

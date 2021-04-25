# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:30:02 2021

@author: Nassim
"""

import os
from tkinter import *
from tkinter import filedialog, ttk

import esat


def main():
    root = Tk()
    root.title("ESAT")
    root.configure(bg="lightsteelblue")
    root.geometry("800x400")

    main_folder = filedialog.askdirectory()
    welcome_label = Label(
        root, text="Welcome!", font=("Helvetica", 12), bg="lightsteelblue"
    ).grid(column=1, row=0)

    starts = []
    stops = []
    folders = [folder for folder in os.listdir(main_folder)]

    input_frame = Frame(root, bg="lightsteelblue")
    input_frame.grid(column=0, row=1)

    head_label = Label(input_frame, text="Filenames", bg="lightsteelblue")
    head_label.grid(column=0, row=2, columnspan=3)

    start_label = Label(input_frame, text="Time of first [h]", bg="lightsteelblue")
    start_label.grid(column=2, row=3)

    stop_label = Label(input_frame, text="Time of last [h]", bg="lightsteelblue")
    stop_label.grid(column=3, row=3)

    for index, folder in enumerate(folders):
        row = index + 5

        fold_label = Label(input_frame, text=folder, bg="lightsteelblue", width=5)
        fold_label.grid(column=1, row=row)

        start_entry = Entry(input_frame, borderwidth=3)
        start_entry.grid(column=2, row=row)
        starts.append(start_entry)

        stop_entry = Entry(input_frame, borderwidth=3)
        stop_entry.grid(column=3, row=row)
        stops.append(stop_entry)

    sma_entry = Entry(input_frame, borderwidth=3)
    sma_entry.grid(column=2, row=row + 1)

    sma_label = Label(
        input_frame,
        text="Weight of point in simple moving average",
        bg="lightsteelblue",
    )
    sma_label.grid(column=1, row=row + 1)

    grow_entry = Entry(input_frame, borderwidth=3)
    grow_entry.grid(column=2, row=row + 2)
    grow_label = Label(input_frame, text="Maximum growth", bg="lightsteelblue")
    grow_label.grid(column=1, row=row + 2)

    shrink_entry = Entry(input_frame, borderwidth=3)
    shrink_entry.grid(column=2, row=row + 3)
    shrink_label = Label(input_frame, text="Maximum collaps", bg="lightsteelblue")
    shrink_label.grid(column=1, row=row + 3)

    def init():

        import imp

        imp.reload(esat)
        print("reloaded esat")
        tstart = []
        teind = []
        
        if len(folders) == 0:
            print('One folder found')
            
            start = float(starts[0].get())
            stop = float(stops[0].get())
            tstart.append(start)
            teind.append(stop)
            
        else:
            for i in range(len(folders)):
                print('Multiple folders found')
                tstart.append(float(starts[i].get()))
                teind.append(float(stops[i].get()))
        try:
            weight = int(sma_entry.get())
            growth = float(grow_entry.get())
            shrink = float(shrink_entry.get())
            esat.run(
                main_folder, tstart, teind, weight=weight, growth=growth, shrink=shrink
            )
        except ValueError:
            esat.run(main_folder, tstart, teind)

    run_but = Button(input_frame, text="Run analysis", borderwidth=3, command=init)
    run_but.grid(column=3, row=row + 1)

    def restart():

        new_main = filedialog.askdirectory()
        if new_main == main_folder:
            pass
        else:
            for widget in input_frame.winfo_children():
                widget.destroy()
            main()

    def help_text():
        help_frame = Frame(root, height=800, width=400)
        help_frame.grid(column=0, row=0)
        help_label = Label(
            help_frame,
            text="""Welcome to this Embryonic Structure Analysis Tool, or ESAT for short. To help you with this application, here are some basic instructions: 
          With the button \'Open files\', under the Files menu, you can browse 
          through your computer to select the folder where the pictures you want 
          to be analysed are saved. 
          Please note, for the analysis to work properly it is essential that you 
          select a folder which contains a (or multiple) folder(s) which contains
          the images to be analysed. For example, we have folder "Embryos" which
          contains 3 folders "embryo_1", "embryo_2" and ""embryo_3", 
          each of these folders contains a certain amount of pictures. 
          We now can select the "Embryos" main folder to run the analysis 
          on all 3 embryos seperately.
          In the box \'Time of first\', fill in the number situated on 
          the bottom left corner of the first picture. And in the entry box 
          \'Time of last\', fill in the number situated on the bottom left corner 
          of the last picture. Note: Please use '.' to separate decimal numbers.
          To configure the trend line this method uses a simple moving average,
          which is calculated using a /weight/, this weight can be adjusted in
          the main menu where you fill in the start and end times. If you do not
          want to adjust the weight you can leave the inut box empty, the default
          weight is 10. Note: The simple moving average is calculated by looking in 
          a window of /weight/ which means that the last "weight"-th points of 
          the measurements are not included in the simple moving average.
          Furthermore the prefered maximum growth and collaps of the embryo are 
          adjustable in the entry boxes below the weight entry box. The growth 
          limits the difference between 2 data points, e.g. if a data point is 
          greater than [growth entry]*[previous data point], this data point is excluded from
          the results, the default is 2. For the collaps entry this formula is
          [previous data point]/[collaps entry], default is also 2.
          By default we mean that if the entry boxes for the weight, growth and collaps
          are left empty, the default value is used.
          The results are automatically exported in the same location as the main folder
          in the form of an excel table with 2 sheets, the first sheet gives a column of all 
          measured surface aresas of all folders, the second contains the slopes 
          and collapses of each folder. Note: the collapses are given in (x, %) format
          which means it will be 2 numbers per cell seperated by a ',' the first number
          represents the time point at which the collaps is initiated and the second is
          the percentage of the collaps. Last a folder with the name [selected_folder]_analysed
          is added to the directory, which will contain a folder per embryo holding
          all of the images with the detected circles drawn in them, and a folder 
          containing the plots of all embryos.""",
            font=("helvetica", 9),
            bg="lightsteelblue",
        ).grid(column=1, row=0)

        back_button = Button(
            help_frame,
            text="Back to analysis",
            bg="lightsteelblue",
            command=help_frame.destroy,
        )
        back_button.grid(column=0, row=0)

    root.option_add("*tearOff", FALSE)
    menu = Menu(root)
    root.config(menu=menu)

    subfile = Menu(menu)
    menu.add_cascade(menu=subfile, label="Folders")
    subfile.add_command(label="open", command=restart)
    # subfile.add_command(label='close', command = restart_program)
    # optie: change file als blijkt dat cirkel niet goed is

    # sub-dropdown-menu
    subhelp = Menu(menu)
    menu.add_cascade(menu=subhelp, label="Help")
    subhelp.add_command(label="Help", command=help_text)
    # helpfunctie koppelen aan dit submenu

    root.mainloop()


def gridit(item, row, column):
    item.grid(column=column, row=row)

main()
"""
15- 37.1/50.7
20- 3/29.3
25- 8.8/50.8
31- 1.4/23.2
5- 18.5/ 43.4
"""

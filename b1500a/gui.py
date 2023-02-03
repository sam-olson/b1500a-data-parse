import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tkinter as tk
from tkinter import filedialog as fd

from b1500a.config import UNITS
from b1500a.parse import IVSweep, GateSweep
from b1500a.utils import avg_lin_fit, avg_parab_fit

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master = master
        self.grid(column=0, row=0)

        self.folder = ""
        self.files = []
        self.file_names = []
        self.file_objects = []
        
        self._build_frames()
        self._place_file_input_frame()
        self._place_mod_frame()
        self._place_plot_frame()

    def _build_frames(self):
        """
        Method for building out sub-frames
        """

        self.file_input_frame = tk.LabelFrame(self)
        self.file_input_frame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky="wens")

        self.mod_frame = tk.LabelFrame(self)
        self.mod_frame.grid(column=0, row=3, columnspan=3, rowspan=3, sticky="wens")

        self.plot_frame = tk.LabelFrame(self)
        self.plot_frame.grid(column=0, row=6, columnspan=3, rowspan=4, sticky="wens")

    def _place_file_input_frame(self):
        """
        Method for placing file input frame
        """

        self.test_type_label = tk.Label(self.file_input_frame, text="Select test type:")
        self.test_type_label.grid(column=0, row=0, columnspan=1, sticky="wens")

        self.test_type_str = tk.StringVar(self.file_input_frame)
        self.test_type_str.set("IV Sweep")

        self.test_type_dd = tk.OptionMenu(self.file_input_frame, self.test_type_str, *["IV Sweep", "Gate Sweep"])
        self.test_type_dd.grid(column=1, row=0, columnspan=2, sticky="wens")

        """
        self.load_file_label = tk.Label(self.file_input_frame, text="Select file folder:")
        self.load_file_label.grid(column=0, row=1, columnspan=1, sticky="wens")
        """

        self.choose_folder_button = tk.Button(self.file_input_frame, text="Select data folder", command=self._choose_folder)
        self.choose_folder_button.grid(column=0, row=1, columnspan=3, sticky="wens")

    def _place_mod_frame(self):
        """
        Method for placing modification frame
        """

        # selected file name variable
        self.file_name_str = tk.StringVar(self.mod_frame)
        self.file_name_str.set(", ".join(self.file_names))

        # displaying selected files
        tk.Label(self.mod_frame, text="Selected files: ").grid(column=0, row=2, columnspan=3, sticky="wens")
        self.file_name_label = tk.Label(self.mod_frame, text=self.file_name_str.get())
        self.file_name_label.grid(column=0, row=3, columnspan=3, sticky="wens")

        # voltage units
        self.volt_units_label = tk.Label(self.mod_frame, text="Voltage Prefix: ")
        self.volt_units_label.grid(column=0, row=4, columnspan=1, sticky="wens")
        self.volt_units_str = tk.StringVar(self.mod_frame)
        self.volt_units_str.set("")
        self.volt_units_dd = tk.OptionMenu(self.mod_frame, self.volt_units_str, *list(UNITS.keys()))
        self.volt_units_dd.grid(column=1, row=4, columnspan=2, sticky="wens")

        # current units
        self.curr_units_label = tk.Label(self.mod_frame, text="Current Prefix: ")
        self.curr_units_label.grid(column=0, row=5, columnspan=1, sticky="wens")
        self.curr_units_str = tk.StringVar(self.mod_frame)
        self.curr_units_str.set("")
        self.curr_units_dd = tk.OptionMenu(self.mod_frame, self.curr_units_str, *list(UNITS.keys()))
        self.curr_units_dd.grid(column=1, row=5, columnspan=2, sticky="wens")

    def _place_plot_frame(self):
        """
        Method for placing plot frame
        """

        # option for displaying fit
        self.fit_var = tk.IntVar(self.plot_frame, value=0)
        self.fit_cb = tk.Checkbutton(self.plot_frame, variable=self.fit_var, text="Fit?")
        self.fit_cb.grid(column=0, row=6, columnspan=1, sticky="wens")

        # option for saving CSV file
        self.csv_var = tk.IntVar(self.plot_frame, value=1)
        self.csv_cb = tk.Checkbutton(self.plot_frame, variable=self.csv_var, text="Save .csv?")
        self.csv_cb.grid(column=1, row=6, columnspan=1, sticky="wens")

        # option for single vs. multiple plots
        self.plot_num_var = tk.IntVar(self.plot_frame, value=1)
        self.plot_num_cb = tk.Checkbutton(self.plot_frame, variable=self.plot_num_var, text="Single plot?")
        self.plot_num_cb.grid(column=2, row=6, columnspan=1, sticky="wens")

        # save folder entry
        tk.Label(self.plot_frame, text="Save folder: ").grid(column=0, row=7, columnspan=1, sticky="wens")
        self.save_folder_var = tk.StringVar(self.plot_frame)
        self.save_folder_var.set("")
        self.save_folder_entry = tk.Entry(self.plot_frame, textvariable=self.save_folder_var)
        self.save_folder_entry.grid(column=1, row=7, columnspan=2, sticky="wens")

        # finish button
        self.done_button = tk.Button(self.plot_frame, text="Finish", command=self._finish)
        self.done_button.grid(column=0, row=8, columnspan=3, sticky="wens")

    def _choose_folder(self):
        """
        Choose folder button handler
        """

        self.folder = fd.askdirectory()
        if self.folder:
            self.file_names = [i for i in os.listdir(self.folder) if i.endswith(".csv")]
            self.files = [os.path.join(self.folder, i) for i in self.file_names]
            self.save_folder_var.set(os.path.join(self.folder, "modified_csv"))
        self.file_name_label["text"] = ",\n".join(self.file_names)

        test_type = self.test_type_str.get()

        if test_type == "IV Sweep":
            self.file_objects = [IVSweep(i) for i in self.files]
        elif test_type == "Gate Sweep":
            self.file_objects = [GateSweep(i) for i in self.files]

    def _finish(self):
        """
        Finish button handler
        """

        # adjust units
        for i in self.file_objects:
            i.change_units("V", self.volt_units_str.get())
            i.change_units("I", self.curr_units_str.get())

        # saving .csv files
        if self.csv_var:
            if self.save_folder_var.get():
                if not os.path.exists(self.save_folder_var.get()):
                    os.makedirs(self.save_folder_var.get())
                for i in self.file_objects:
                    i.save_csv(os.path.join(self.save_folder_var.get(), i.fname))
            else:
                print("Save folder location not specified!")

        # saving stats
        if self.test_type_str.get() == "IV Sweep":
            test_name = []
            res = []
            for i in self.file_objects:
                test_name.append(i.fname)
                res.append(i.resistance)
            test_name.append("average")
            res.append(np.mean(res))
            pd.DataFrame(data={"Test": test_name, "Resistance (ohms)": res}).to_csv(os.path.join(self.save_folder_var.get(), "stats.csv"), index=False)

        elif self.test_type_str.get() == "Gate Sweep":
            test_name = []
            dirac = []
            for i in self.file_objects:
                test_name.append(i.fname)
                dirac.append(i.dirac)
            test_name.append("average")
            dirac.append(np.mean(dirac))
            pd.DataFrame(data={"Test": test_name, "Dirac Point (V)": dirac}).to_csv(os.path.join(self.save_folder_var.get(), "stats.csv"), index=False)
 
        # plotting 
        if self.plot_num_var.get():
            for i in self.file_objects:
                plt.plot(i.volts, i.current, label=f"{i.metadata['DeviceName']}-{i.metadata['RunNum']}")
            if self.fit_var:
                if self.test_type_str.get() == "IV Sweep":
                    plt.plot(*avg_lin_fit([[i.volts, i.current] for i in self.file_objects]), color="black", linestyle="--", label="fit")
                elif self.test_type_str.get() == "Gate Sweep":
                    plt.plot(*avg_parab_fit([[i.volts, i.current] for i in self.file_objects]), color="black", linestyle="--", label="fit")
            plt.xlabel(f"Voltage ({self.volt_units_str.get()}V)")
            plt.ylabel(f"Current ({self.curr_units_str.get()}A)")
            plt.legend()
            plt.show()
        else:
            for i in self.file_objects:
                plt.plot(i.volts, i.current)
                plt.show()



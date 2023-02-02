import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from b1500a.config import UNITS
from b1500a.utils import extract_metadata

class DataFile:
    def __init__(self, fpath, smus=3):
        """
        Base class for parsing Agilent B1500A data files

        Parameters
        ----------
        fpath: path to file of interest
        smus: number of source/measurement units equipped on the B1500A (default is 3)
        """

        self.fpath = fpath
        self.fname = os.path.basename(fpath)
        self.smus = smus
        self.metadata = extract_metadata(os.path.basename(fpath))
        self.volts = []
        self.current = []

        self.column_names = ["Category", "Measurement"] + [f"SMU{i}" for i in range(1, self.smus+1)]
        self.all_data = pd.read_csv(self.fpath, names=self.column_names)
        
        self.data_col_names = np.array(self.all_data[self.all_data["Category"] == "DataName"].iloc[0].dropna())
        self.meas_data = self.all_data[self.all_data["Category"] == "DataValue"].dropna(axis=1).reset_index(drop=True)
        self.meas_data = self.meas_data.rename(columns={i:j.strip() for i,j in zip(self.meas_data.columns, self.data_col_names)})

class IVSweep(DataFile):
    def __init__(self, fpath, smus=3, volt="DrainV", curr="DrainI"):
        super().__init__(fpath, smus)
        self.volts = [float(i) for i in self.meas_data[volt]]
        self.current = [float(i) for i in self.meas_data[curr]]
        self.volt_units = ""
        self.current_units = ""

        self.fit = np.polyfit(self.volts, self.current, 1)
        self.resistance = 1/self.fit[0]

        self.v_fit = np.arange(self.volts[0], self.volts[-1], (self.volts[-1]-self.volts[0])/len(self.volts))
        self.i_fit = [(i*self.fit[0])+self.fit[1] for i in self.v_fit]

    def plot(self, fit=False, save=False, show=False, color="blue"):
        plt.plot(self.volts, self.current, color=color, label=self.metadata["DeviceName"])
        if fit:
            plt.plot(self.v_fit, self.i_fit, linestyle="--", color="black")

        plt.legend()

        if save:
            plt.savefig(save)

        if show:
            plt.show()

    def change_units(self, parameter, unit):
        if parameter.upper() == "V":
            if self.volt_units != "":
                self.volts = [i*UNITS[unit] for i in self.volts]
                self.v_fit = [i*UNITS[unit] for i in self.v_fit]
            self.volts = [i/UNITS[unit] for i in self.volts]
            self.v_fit = [i/UNITS[unit] for i in self.v_fit]
            self.volt_units = unit
        elif parameter.upper() == "I":
            if self.current_units != "":
                self.current = [i*UNITS[unit] for i in self.current]
                self.i_fit = [i*UNITS[unit] for i in self.i_fit]
            self.current = [i/UNITS[unit] for i in self.current]
            self.i_fit = [i/UNITS[unit] for i in self.i_fit]
            self.current_units = unit
        else:
            print(f"Bad value for 'parameter' ({parameter}), should be 'V' for volts or 'I' for current")

    def save_csv(self, fpath):
        """
        Method for saving a simpler .csv file

        Parameters
        ----------
        fpath: file path to save to
        """
        pd.DataFrame(data={f"Volts ({self.volt_units}V)": self.volts, f"Current ({self.current_units}A)": self.current}).to_csv(fpath, index=False)


class GateSweep(DataFile):
    def __init__(self, fpath, smus=3, volt="GateV", curr="DrainI"):
        super().__init__(fpath, smus)
        self.volts = [float(i) for i in self.meas_data[volt]]
        self.current = [float(i) for i in self.meas_data[curr]]
        self.volt_units = ""
        self.current_units = ""

        self.fit = np.polyfit(self.volts, self.current, 2)
        self.dirac = -self.fit[1]/(2*self.fit[0])

        self.v_fit = np.arange(self.volts[0], self.volts[-1], (self.volts[-1]-self.volts[0])/len(self.volts))
        self.i_fit = [(i*i*self.fit[0])+(i*self.fit[1])+self.fit[2] for i in self.v_fit]

    def plot(self, fit=False, save=False, show=False, color="blue"):
        plt.plot(self.volts, self.current, color=color, label=self.metadata["DeviceName"])

        if fit:
            plt.plot(self.v_fit, self.i_fit, linestyle="--", color="black")

        plt.legend()

        if save:
            plt.savefig(save)
        if show:
            plt.show()

    def change_units(self, parameter, unit):
        if parameter.upper() == "V":
            if self.volt_units != "":
                self.volts = [i*UNITS[unit] for i in self.volts]
                self.v_fit = [i*UNITS[unit] for i in self.v_fit]
            self.volts = [i/UNITS[unit] for i in self.volts]
            self.v_fit = [i/UNITS[unit] for i in self.v_fit]
            self.volt_units = unit
        elif parameter.upper() == "I":
            if self.current_units != "":
                self.current = [i*UNITS[unit] for i in self.current]
                self.i_fit = [i*UNITS[unit] for i in self.i_fit]
            self.current = [i/UNITS[unit] for i in self.current]
            self.i_fit = [i/UNITS[unit] for i in self.i_fit]
            self.current_units = unit
        else:
            print(f"Bad value for 'parameter' ({parameter}), should be 'V' for volts or 'I' for current")

    def save_csv(self, fpath):
        """
        Method for saving a simpler .csv file

        Parameters
        ----------
        fpath: file path to save to
        """
        pd.DataFrame(data={f"Volts ({self.volt_units}V)": self.volts, f"Current ({self.current_units}A)": self.current}).to_csv(fpath, index=False)


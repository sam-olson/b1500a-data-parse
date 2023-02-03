# b1500a-data-parse

A simple Python GUI that helps process output files from an Agilent B1500A semiconductor parameter analyzer (SPA). This SPA is used in my lab to analyze graphene-based transistors. When it saves .csv files of test data, there is a large quantity of metadata included in the files that can be painful to work around when processing large quantities of data. This GUI parses the files automatically and saves a simpler version of the data.

This program includes the ability to process:
- IV sweeps
- Gate voltage sweeps

Some features...
- Averages multiple runs
- Fits lines (IV sweep) or parabolas (gate sweep)
- Calculates resistance (IV sweep) or dirac point (gate sweep)
- Outputs simple .csv file for further investigation (i.e., in Excel)

More tests and features will be added as required.

## Usage
Download or clone this repository, install the requirements in `requirements.txt` and run the program:
```shell
python3 app.py
```

In the GUI, select a folder containing multiple B1500A test files (in .csv format) of the same kind (for example multiple IV sweeps of the same device). The GUI then presents options for plotting and saving the data.

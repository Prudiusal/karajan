from os import environ
import csv
import tkinter
from tkinter import filedialog
from pathlib import Path
tkinter.Tk().withdraw()


def check_and_update_plugin_paths(environments: list):
    """
    Checks the env.csv file for the record of the environment path.
    Asks to choose the path in the explorer, if there is no corresponding record.

    Args:
        environments - list of environment variables, required to be set.
    """
    if Path('env.csv').exists():
        with open('env.csv', 'r', newline='\n') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[0] in environments:
                    environ[row[0]] = row[1]
                    environments.remove(row[0])

    with open('env.csv', 'a', newline='\n') as f:
        writer = csv.writer(f, delimiter=',')
        for var in environments:
            path = filedialog.askopenfile(title=f'Choose the path to the {var} plugin').name
            environ[var] = path
            writer.writerow([var, path])

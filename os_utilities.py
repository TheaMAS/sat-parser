
# This file contains file access and os related utilities used by many
#   functions in many files.

import os
from sys import platform

import pandas as pd

LINUX = 0
OSX = 1
WINDOWS = 2

#Is this thing a file?
def file_check(fn):
	try:
		open(fn, "r")
		return 1
	except IOError:
		print("Error: Needs a file")
		return 0

def read_file(fn):
    """
    This function opens a file and returns all the data as a string.
    """
    data = ""
    with open(fn) as f:
        data = f.read()
    return data;

def get_csv_data(csv_location):
    """
    This functions reads in a csv file and returns a pandas csv object.
    """
    return pd.read_csv(csv_location)

def check_os():
    if platform == "linux" or platform == "linux2":
        return LINUX
        # linux
    elif platform == "darwin":
        return OSX
        # OS X
    elif platform == "win32":
        return WINDOWS
        # Windows...

    return None

# print(check_os())

def get_csv_files(folder):
    filepaths = []

    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and f.endswith(".csv"):
            filepaths.append(f)
    return filepaths

def get_ext_files(folder, ext):
    """
    Returns a list of all files in a given folder with given extension.

    get_ext_files("./outputs/", "tle")
    """
    filepaths = []

    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and f.endswith("." + ext):
            filepaths.append(f)

    return filepaths


def save_to_outputs_file(content, filename, extension):
	f = open("./outputs/" + filename + "." + extension, "w")
	f.write(content)
	f.close()
	return 0


def make_folder(path):
	if not os.path.exists(path):
		os.makedirs(path)

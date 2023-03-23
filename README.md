# Using This Repository

This repo contains several libraries that serve to perform calculations and analysis on Time-Varying Graphs (TVGs) generated from orb-derived CSV files. Below are steps on how to begin to code using this library, as well as pointers to documentation for library specifics.

## Prerequisites/Dependencies

This package has several dependencies, which at the moment do not come automatically installed. If your code does not immediately work, check the terminal error message to see if Python does not recognize a name. To resolve this, typically running "pip install *name*" will resolve the issue.

### A Cautionary Tale for Windows

The library graph_tool is known to not play nicely with Windows. Therefore, if issues involving pandas come up, and you are on a Windows machine, this may be the reason. 

## Generating an ORB file from scratch

This repo comes equipped with a number of csv files for testing, but can technically work with any orb file. To generate orb files for later use, you can create a script using the functions in *sim_builder.py*. 

### Sample Script

    import sim_builder as sb
    
    sb.generate_moon_starlink_simulations('simulations', 10, 7)

The above-script will create a folder *simulations*, and fill it with 10 orb files of simulated systems with 5 moon satellites and 7 Starlink satellites. Additionally, a bash script file will be generated that the user can run to create *csv* files out of the *orb* files. If you are on Linux, running this file will invoke SOAP, opening each *orb* file. See the section **Generating a CSV File from an ORB file** for more details.

All *sim_builder* generator functions work in this way. Here is a list of useful functions from this library, along with a short description of their parameters and outputs:

- generate_moon_tdrs_simulations(folder_name, n, k)
-- Generates n simulations with 5 moon satellites and k TDRS satellites
- generate_moon_starlink_simulations(folder_name, n, k)
-- Generates n simulations with 5 moon satellites and k Starlink satellites
- generate_moon_starlink_ground_simulations(folder_name, n, k)
-- Generates n simulations with 5 moon satellites, k Starlink satellites, and 2 ground stations (currently Albany, NY and Sydney Australia)


## Generating a CSV File from an ORB file

Suppose you already have an *orb* file; you will need to turn it into a csv file in order for it to be useful. Conveniently, SOAP does this for us. Simply open the *orb* file in SOAP and it should generate a *csv* file based on the *orb* file you opened. 

If you have just run a script using a *sim_builder* generating function, that should come with a bash script file (ending in *.sh*). If you are running a \*nix operating system (Linux, Mac, Unix), just run this script in your preferred terminal. If your system is configured to open *.orb* files with SOAP, it will automate opening these files and producing the desired CSV files.


## Importing Your CSV

Now that you have a *.csv* file that you want to play (read: work) with, you'll want a way to get it into your code. To do this, you'll want to import the Interval Matrix Algebra Calculator - the main library of this repository. The function to process a *.csv* file is called *soapConverter*. Here is some sample code that demonstrates:

    import Interval_Matrix_Algebra_Calculator_v0 as imac
    
    A = imac.soapConverter('path/to/file.csv')
    A = remove_diagonal(A)
    A_2 = matrix_k_walk(A, 2)

This script imports a formatted csv file and turns it into a matrix of intervals, and then performs a number of operations and calculations on the matrix. See the documentation on available functions for more information on what calculations can be performed.


## Conda Environment

Run `conda env create --file environment.yml` and `conda activate sat-parser` to manage dependencies.

You need `cmake` and `boost` installed for `dionysus` to install properly.
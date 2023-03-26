
from os_utilities import *
from orb_builder import *
from report_parser import *
import file_parser as fp
import time_utilities as tu

import subprocess
import time
import matrix
import random
from sys import platform
from itertools import islice


import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fh = logging.FileHandler("./outputs/benchmarks.log")
fh.setLevel(logging.INFO)
logger.addHandler(fh)

def execute_commands(commands, hacks, max_workers = 10, randomize=False):
    """
    This function runs all the terminal commands specified in `commands` on
        `max_workers` cores / threads.
    """
    logger.info(f"Running `execute_commands` with {len(commands)} commands and {len(hacks)} hacks.")

    if randomize:
        random.shuffle(commands)

    processes = (subprocess.Popen(cmd) for cmd in commands)
    running_processes = list(islice(processes, max_workers))  # start new processes

    while running_processes:
        for i, process in enumerate(running_processes):
            if process.poll() is not None:  # the process has finished
                running_processes[i] = next(processes, None)  # start new process
                if running_processes[i] is None: # no new processes
                    del running_processes[i]
                    break
            else:
                time.sleep(0.5)

                for hack in hacks:
                    subprocess.run(hack)        

    return None

def run_soap_mac(orb_paths, max_workers = 10):
    """
    This function prepares the macOS-specific commands to be run and any
        hacks that are needed to get around soap specific bugs.
    """
    logger.info(f"Running `run_soap_mac` with {len(orb_paths)} simulations on {max_workers} threads.")

    osascript_unfocus = [
        'osascript',
        '-e',
        'tell application "System Events"',
        '-e',
        'set visible of application process "SOAP" to false',
        '-e',
        'end tell'
    ]

    osascript_focus = [
        'osascript',
        '-e',
        'tell application "System Events"',
        '-e',
        'tell process "SOAP"',
        '-e',
        'set frontmost to true',
        '-e',
        'end tell',
        '-e',
        'end tell'
    ]

    commands = []
    for path in orb_paths:
        # args = ["open", "-n", "-W", f"{folder}/{filename}"]
        args = ["open", "-n", "-j", "-W", path]
        commands.append(args)

    # print(f"len(commands)={len(commands)}")

    hacks = [osascript_unfocus, osascript_focus]
    execute_commands(commands, hacks, max_workers)
    
    return None

def run_soap_linux():

    return None

def generate_benchmark(name, n_list, sample_size, max_workers = 12):
    start_absolute = time.perf_counter()

    # n_list = [10, 15, 20, 40, 60, 100, 150, 200, 250, 500]
    # n_list = [5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200]
    # n_list = [20]
    # sample_size = 30

    orb_paths = [] # used to keep track of what files to feed into soap

    starlink = build_satellites_csv("starlink")

    folder_base = f"./outputs/benchmarks"
    make_folder(folder_base)

    # TODO : following can be parallelized
    for n in n_list:
        folder_name = f"starlink-{n}-sat-{name}"
        make_folder(f"{folder_base}/{folder_name}")

        logger.info(f"Generating {sample_size} simulations of {n} satellites.")
        
        start = time.perf_counter()

        for i in range(sample_size):
            name = f"starlink_{n}_sats_{i}"

            satellites = sample_sats(starlink, n)
            orb_paths.append(f"{folder_base}/{folder_name}/{name}.orb")

            save_to_outputs_file(
                generate_orb(satellites, name),
                # generate_orb(satellites, name, date=tu.get_random_date()),
                f"benchmarks/{folder_name}/{name}", "orb")
        
        end = time.perf_counter()

        logger.info(f"\t({end - start} seconds)")

    if platform == "darwin":
        print("MACOS")

    logger.info(f"Running {len(orb_paths)} soap simulations")
    start = time.perf_counter()

    run_soap_mac(orb_paths, max_workers=15)

    end = time.perf_counter()
    logger.info(f"\t({end - start} seconds)")

    logger.info(f"Parsing {len(orb_paths)} Contact Analysis Reports")
    start_out = time.perf_counter()

    # TODO : following can be parallelized
    for path in orb_paths:
        # print(path)
        start = time.perf_counter()
        A = fp.soap_converter(path.replace(".orb", " Contact Analysis.csv"))

        # TODO : calculate powers,
        end = time.perf_counter()

        logger.info(f"\t\tdim({path.split('/')[-1].replace('.orb', '')}) = {A.dim_row}x{A.dim_col} ({end - start} seconds)")
        # print(f"dim(A) = {A.dim_row}x{A.dim_col}")
    end_out = time.perf_counter()
    logger.info(f"\t({end_out - start_out} seconds)")
    # go through all of them with orb_parser and soap_converter

    end_absolute = time.perf_counter()
    logger.info(f"Total runtime : {end_absolute - start_absolute} seconds")

    return None

if __name__ == "__main__":
    n_list = [5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200]
    # n_list = [50]
    generate_benchmark("single", n_list, sample_size=30, max_workers=15)
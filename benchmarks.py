
from os_utilities import *
from orb_builder import *
from report_parser import *
import file_parser as fp
import time_utilities as tu
import soap_utilities as su
import matrix

import time
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fh = logging.FileHandler("./outputs/benchmarks.log")
fh.setLevel(logging.INFO)
logger.addHandler(fh)

def generate_benchmark(name, n_list, sample_size, max_workers = 12):
    start_absolute = time.perf_counter()

    orb_paths = [] # used to keep track of what files to feed into soap

    starlink = build_satellites_csv("starlink")
    moon_sats = get_moon_platforms()
    mars_sats = get_mars_platforms()
    ground = [
        create_ground_object_dictionary("Ground-Albany", 42.685012663456163, -73.82479012295363, 0),
        create_ground_object_dictionary("Ground-Sydney", -33.868888888888889, 151.20939697339508, 0)
    ]
    norad = build_satellites_from_tle("./sources/tdrss.tle")

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

            # satellites = sample_sats(starlink + moon_sats + mars_sats + ground + norad, n)
            satellites = sample_sats(starlink, n)
            orb_paths.append(f"{folder_base}/{folder_name}/{name}.orb")

            save_to_outputs_file(
                generate_orb(satellites, name),
                # generate_orb(satellites, name, date=tu.get_random_date()),
                f"benchmarks/{folder_name}/{name}", "orb")
        
        end = time.perf_counter()

        logger.info(f"\t({end - start} seconds)")

    # if platform == "darwin":
    #     print("MACOS")

    logger.info(f"Running {len(orb_paths)} soap simulations")
    start = time.perf_counter()

    su.run_soap_mac(orb_paths, max_workers=15)

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
    n_list = [5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 500]
    n_list = [1000]
    # n_list = [50]
    generate_benchmark("single", n_list, sample_size=10, max_workers=10)

# TODO : plot first 56 starlinks to see if band is visible
# TODO : separate v14 and v15 templates
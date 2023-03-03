
from os_utilities import *
from orb_builder import *

if __name__ == "__main__":
    DEBUG = True;
else:
    DEBUG = False

def generate_bash(folder_name, prefix, n):
    """
    This generates a bash file which can then be used to open all the orb
    files in a given folder with soap. The orb files are defined in such a
    way that soap runs the contact analysis and saves the output as a csv,
    then closes soap.
    """

    base_path = ""
    command = "wine"
    soap_path = base_path + "\".wine/drive_c/SOAP/bin64/soap.exe\" "

    if check_os() == OSX:
        command = "open"
        soap_path = ""

    outputs_path = "./outputs/"

	# TODO : make .sh file to run all sims
	# wine ".wine/drive_c/SOAP/bin64/soap.exe" "./norad.orb"
    starlink_bash = "#!/bin/bash" + "\n"
    for i in range(n):
        starlink_bash += "" + command + " " + soap_path + \
            "\"" + outputs_path + \
            folder_name + "/" + prefix + "_" + str(i) + ".orb\"" + "\n"
    save_to_outputs_file(
        starlink_bash,
        folder_name + "/" + prefix + "_" + str(n),
        "sh")

    return None

# generate_bash("starlink-7", "starlink", 10)

def generate_general_bash(folder_name):
    starlink_bash = """
#!/bin/bash

for f in ./*.orb; do
    # do some stuff here with "$f"
    # remember to quote it or spaces may misbehave
    wine ".wine/drive_c/SOAP/bin64/soap.exe" "$f"
done
    """


# exit()

# base = ""
# command = "open"
# # command = "wine"
# soap_path = base + "\".wine/drive_c/SOAP/bin64/soap.exe\""
# soap_path = ""
# outputs_path = base + "./outputs/"


# n = number of simulations
# k = sample size
def generate_simulations(n, k, folder_name):
    satellites = build_satellites_csv("starlink")
    make_folder("./outputs/" + folder_name)

    prefix = "starlink"

    for i in range(n):
        name = prefix + "_" + str(i)
        subset = sample_sats(satellites, k)
        save_to_outputs_file(
            generate_orb(subset, name),
            folder_name + "/" + name,
            "orb")
        # print(i)

    generate_bash(folder_name, prefix, n);

	# TODO : make .sh file to run all sims
	# wine ".wine/drive_c/SOAP/bin64/soap.exe" "./norad.orb"
	# starlink_bash = "#!/bin/bash" + "\n"
	# for i in range(n):
	# 	starlink_bash += "" + command + " " + soap_path + \
	# 		"\"" + outputs_path + \
	# 		folder_name + "/" + prefix + "_" + str(i) + ".orb\"" + "\n"
	# save_to_file(
	# 	starlink_bash,
	# 	folder_name + "/" + prefix + "_" + str(n),
	# 	"sh")

    return None

# generate_simulations(2, 6, "starlink-6");
# generate_simulations(10, 10, "starlink-10");

def generate_moon_tdrs_simulations(folder_name, n, k):
    """
    We generate `n` simulations with five moon satellites and `k` out of
    ten TDRS satellites.
    """
    assert(k <= 10)

    make_folder("./outputs/" + folder_name)

    prefix = "moonsim"

    tdrs = get_tdrs_platforms()
    moon_sats = get_moon_platforms()

    for i in range(n):
        name = prefix + "_" + str(i)

        subset = sample_sats(tdrs, k)
        satellites = subset + moon_sats
        save_to_outputs_file(
            generate_orb(satellites, name),
            folder_name + "/" + name,
            "orb")
        # print(i)

    generate_bash(folder_name, prefix, n);

    return None

# generate_moon_tdrs_simulations("moonsim-10", 10, 5)

def generate_moon_starlink_simulations(folder_name, n, k):
    """
    We generate `n` simulations with five moon satellites and `k` out of
    many starlink satellites.
    """

    make_folder("./outputs/" + folder_name)

    prefix = "moonsim"

    starlink = build_satellites_csv("starlink")
    moon_sats = get_moon_platforms()

    for i in range(n):
        name = prefix + "_" + str(i)

        subset = sample_sats(starlink, k)
        satellites = subset + moon_sats
        save_to_outputs_file(
            generate_orb(satellites, name),
            folder_name + "/" + name,
            "orb")
        # print(i)

    generate_bash(folder_name, prefix, n);

    return None

# generate_moon_starlink_simulations("moonsim-4", 10, 4)

def generate_moon_starlink_ground_simulations(folder_name, n, k):
    """
    We generte `n` simulations with five moon satellites and `k` out of
    many starlink satellites, and two ground stations.
    """

    make_folder("./outputs/" + folder_name)

    prefix = "moongnd"

    starlink = build_satellites_csv("starlink")
    moon_sats = get_moon_platforms()
    ground = [
        create_ground_object_dictionary("Ground:Albany", 42.685012663456163, -73.82479012295363, 0),
        create_ground_object_dictionary("Ground:Sydney", -33.868888888888889, 151.20939697339508, 0)
    ]

    for i in range(n):
        name = prefix + "_" + str(i)

        subset = sample_sats(starlink, k)
        satellites = subset + moon_sats + ground
        save_to_outputs_file(
            generate_orb(satellites, name),
            folder_name + "/" + name,
            "orb")
        # print(i)

    generate_bash(folder_name, prefix, n);

# generate_moon_starlink_ground_simulations("moongnd-5", 5, 3)

def generate_moon_mars_starlink_simulations(folder_name, n, k):
    make_folder("./outputs/" + folder_name)

    prefix = "emm"

    starlink = build_satellites_csv("starlink")
    moon_sats = get_moon_platforms()
    mars_sats = get_mars_platforms()
    ground = [
        create_ground_object_dictionary("Ground:Albany", 42.685012663456163, -73.82479012295363, 0),
        create_ground_object_dictionary("Ground:Sydney", -33.868888888888889, 151.20939697339508, 0)
    ]

    for i in range(n):
        name = prefix + "_" + str(i)

        subset = sample_sats(starlink, k)
        satellites = subset + moon_sats + mars_sats + ground
        save_to_outputs_file(
            generate_orb(satellites, name),
            folder_name + "/" + name,
            "orb")
        # print(i)

    generate_bash(folder_name, prefix, n);

# generate_moon_mars_starlink_simulations("sim-2022-09-28", 5, 89)

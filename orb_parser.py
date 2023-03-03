
from os_utilities import *

def parse_norad(split_line, name):
    """
    Parses the second line in a NORAD platform define in an orb file.
    Expect 16 entries, the first being "STATE".

    STATE {norad_cat_id} {epoch_year} {epoch_fraction} {mean_motion_dot}
        {mean_motion_ddot} {bstar} {ephemeris_type} {element_set_no}
        {inclination} {ra_of_asc_node} {eccentricity} {arg_of_pericenter}
        {mean_anomaly} {mean_motion} {rev_at_epoch}

    """
    # print("Parsing NORAD")
    # print(split_line)
    assert(len(split_line) == 16)

    platform = {}

    platform["object_name"] = name # ex
    platform["norad_cat_id"] = float(split_line[1])
    platform["epoch_year"] = float(split_line[2])
    platform["epoch_fraction"] = float(split_line[3])
    platform["mean_motion_dot"] = float(split_line[4])
    platform["mean_motion_ddot"] = float(split_line[5])
    platform["bstar"] = float(split_line[6])
    platform["ephemeris_type"] = float(split_line[7])
    platform["element_set_no"] = float(split_line[8])
    platform["inclination"] = float(split_line[9])
    platform["ra_of_asc_node"] = float(split_line[10])
    platform["eccentricity"] = float(split_line[11])
    platform["arg_of_pericenter"] = float(split_line[12])
    platform["mean_anomaly"] = float(split_line[13])
    platform["mean_motion"] = float(split_line[14])
    platform["rev_at_epoch"] = float(split_line[15])

    # for entry in split_line[1:]:
    #     print(entry)
    # print(len(split_line))
    # print(platform)
    return platform

def parse_custom(split_line, name, system):
    # print("Parsing CUSTOM")

    assert(len(split_line) == 16)

    platform = {}

    platform["system"] = system
    platform["object_name"] = name
    platform["body"] = split_line[1].strip("\"")
    platform["ic_type"] = split_line[2]
    platform["orbit_type"] = split_line[3]
    platform["semi_major_axis"] = float(split_line[4])
    platform["eccentricity"] = float(split_line[5])
    platform["inclination"] = float(split_line[6])
    platform["ra_of_asc_node"] = float(split_line[7])
    platform["arg_of_pericenter"] = float(split_line[8])
    platform["mean_anomaly"] = float(split_line[9])
    platform["year"] = float(split_line[10])
    platform["month"] = float(split_line[11])
    platform["day"] = float(split_line[12])
    platform["hour"] = float(split_line[13])
    platform["minute"] = float(split_line[14])
    platform["second"] = float(split_line[15])

    # print(len(split_line))
    # print(split_line[1])
    # for entry in split_line:
    #     print(entry)
    # print(platform)

    return platform

def parse_ground(split_line, name):
    # print("Parsing ECR_FIXED")
    assert(len(split_line) == 4)

    platform = {}

    platform["object_name"] = name
    platform["latitude"] = float(split_line[1])
    platform["longitude"] = float(split_line[2])
    platform["altitude"] = float(split_line[3])

    # print(name)
    # print(split_line)
    # print(platform)
    return platform

# https://stackoverflow.com/questions/7866128/
def get_platforms(filename):
    content = read_file(filename)

    d = "DEFINE"
    content = [d+e for e in content.split(d) if e]

    platforms = []
    # content = content.split("DEFINE")
    # for entry in content:
    #     entry = "DEFINE" + entry
    # print(content[0])
    for entry in content:
        # platform = {}
        name = ""
        system = ""

        lines = entry.split("\n")

        first_line = lines[0]
        if first_line.startswith("DEFINE PLATFORM"):

            # print(first_line.split("\""))
            if len(first_line.split("\"")) < 2: continue; # skip no names

            name = first_line.split("\"")[1]
            if name.startswith("."): continue; # skip defaults

            system = first_line.split()[2]

            # print(name)
            # platform["name"] = name

            # print(lines[1].split(" "))
            # print(lines[0])
            # print(entry)

        else: # skip non-platform defines
            continue

        second_line = lines[1].split()
        sl_len = len(second_line)

        if second_line[0] != "STATE" or (sl_len != 4 and sl_len < 14):
            continue; # skip if no TLE

        if "CUSTOM" in second_line or second_line[1].startswith("\""):
            platform = parse_custom(second_line, name, system)
            # print("custom")
        elif sl_len == 4:
            platform = parse_ground(second_line, name)
        else:
            platform = parse_norad(second_line, name)
            # print("norad")
        platforms.append(platform)


        # print(len(second_line)) # 14
        # print(second_line)

        # print(platform)
        # platforms.append(platform)
    # print(platforms)
    return platforms

# platforms = get_platforms("./tests/orb/platforms_moon.orb")
# platforms = get_platforms("./Networking_Example.orb")
# platforms = get_platforms("./outputs/starlink-7/starlink_0.orb")
# platforms = get_platforms("./ground.orb")
# platforms = get_platforms("./outputs/sim-2022-08-26/moongnd_base.orb")

# for platform in platforms:
#     print(platform)
#     print(platform["object_name"])

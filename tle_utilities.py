from sgp4.api import Satrec
from sgp4.api import jday
from sgp4 import omm


from datetime import datetime

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from os_utilities import *

EARTH_RADIUS = 6367 # KM

def starlink_exclude(date, dist_min, dist_max):
    """
    Returns a list of starlink satellites to exclude if they are not within 
        the range [dist_min, dist_max] given in km.
    """
    jd, fr = jday(date.year, date.month, date.day, date.hour, date.minute, date.second)

    starlink_omm = []
    with open("./sources/starlink.csv") as f:
        for entry in omm.parse_csv(f):
            starlink_omm.append(entry)
    
    exclude_list = []
    for entry in starlink_omm:
        sat_name = entry['OBJECT_NAME']

        sat = Satrec()
        omm.initialize(sat, entry)

        e, r, v = sat.sgp4(jd, fr)
        height = np.sqrt(np.sum(np.asarray(r)**2)) - EARTH_RADIUS
        # print(f"{sat_name} height is {height}")
        if height <= dist_min or height >= dist_max:
            # print(f"excluding {sat_name} with height {height}")
            exclude_list.append(sat_name)

    return exclude_list

if __name__ == "__main__":

    # set time to current
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second
    jd, fr = jday(year, month, day, hour, minute, second)

    # fix time for reproduceability
    jd, fr = jday(2022, 5, 24, 16, 23, 56)

    print(jd)
    print(fr)
    # exit()

    date = datetime.strptime("01/08/22 00:00", "%d/%m/%y %H:%M")
    assert(len(starlink_exclude(date, 200, 800)) == 240)


def get_jday(datetime_object):
    year = datetime_object.year
    month = datetime_object.month
    day = datetime_object.day
    hour = datetime_object.hour
    minute = datetime_object.minute
    second = datetime_object.second
    return jday(year, month, day, hour, minute, second)

# def read_file(fn):
# 	data = ""
# 	with open(fn) as f:
#    		data = f.read()
# 	return data;

if __name__ == "__main__":

    tle = """
    TDRS 3
    1 19548U 88091B   22144.45796491 -.00000313  00000+0  00000+0 0  9997
    2 19548  13.7334 351.5139 0036255 336.8078  29.6172  1.00266005110484
    """.strip()
    line_one = tle.split("\n")[1]
    line_two = tle.split("\n")[2]
    satellite = Satrec.twoline2rv(line_one, line_two)
    e, r, v = satellite.sgp4(jd, fr)

    print("Distance is {}".format(np.sqrt(np.sum(np.asarray(r)**2))))
    print("Speed is {}".format(np.sqrt(np.sum(np.asarray(v)**2))))
    # exit()

def get_tles_dict(filepath):
    tles = {}

    tle_data = read_file(filepath)
    tle_lines = tle_data.split("\n")
    n = int(len(tle_lines) / 3)

    for i in range(n):
        j = 3*i
        name = tle_lines[j].strip() # strip leading / trailing whitespace
        line_one = tle_lines[j + 1]
        line_two = tle_lines[j + 2]
        satellite = Satrec.twoline2rv(line_one, line_two)
        tles[name] = satellite

    return tles

if __name__ == "__main__":

    filepath = "./sources/starlink.tle"
    tles = get_tles_dict(filepath)
    # print(tles.keys())
    for id, satellite in tles.items():
        print(id)
        e, r, v = satellite.sgp4(jd, fr)
        break
    # exit()

    # Testing Plotting.

    tle_data = read_file("./sources/starlink.tle")
    tle_list = tle_data.split("\n")

    n = int(len(tle_list) / 3)

    x = []
    y = []
    z = []

    for i in range(n):
        j = 3 * i
        line_one = tle_list[j + 1]
        line_two = tle_list[j + 2]
        satellite = Satrec.twoline2rv(line_one, line_two)

        # error position velocity
        e, r, v = satellite.sgp4(jd, fr)

        # normalize
        r = np.asarray(r)
        normalized_r = r / np.sqrt(np.sum(r**2))
        x.append(normalized_r[0])
        y.append(normalized_r[1])
        z.append(normalized_r[2])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x,y,z)
    # plt.show()
    # print(x)
    # print(len(tle_list))

from datetime import date
from datetime import datetime
from datetime import timedelta
import random 

def epoch_year(epoch_str):
	return epoch_str[2:4]

def epoch_day(epoch_str):
	epoch_date = epoch_str.split("T")[0]
	epoch_list = epoch_date.split('-')
	year = int(epoch_list[0])
	month = int(epoch_list[1])
	day = int(epoch_list[2])

	date_val = date(year, month, day)
	day_of_year = date_val.toordinal() - date(date_val.year, 1, 1).toordinal()
	return int(day_of_year)

def epoch_hour(epoch_str):
	epoch_hours = epoch_str.split("T")[1]
	epoch_list = epoch_hours.split(':')
	hour = float(epoch_list[0])
	minute = float(epoch_list[1])
	second = float(epoch_list[2])
	fraction = (hour / 24) + (minute / (24 * 60)) + (second / (24 * 60 * 60) )
	return fraction

def fraction_to_epoch(fraction):
	hour = fraction * 24
	minutes = (hour - int(hour)) * 60
	seconds = (minutes - int(minutes)) * 60
	print(int(hour), int(minutes), seconds)
	return ""

def epoch_fraction(epoch):
	epoch_str = str(epoch_day(epoch)) + "." + str(epoch_hour(epoch))[2:]
	return epoch_str

if __name__ == "__main__":
	
	# expect : 22 135.33389020999999
	epoch = "2022-05-16T08:10:48.777312"

	# print (orb_epoch(epoch))
	#print (orb_epoch("2022-05-14T11:36:48.540096"))

	# fraction_to_epoch(0.33389020999999);
	# fraction_to_epoch(0.34084233);

	# fraction_to_epoch(6142.39999999999963620)

	universe = "Start: 2022/04/30 01:43:00.00, Stop: 2022/05/01 01:43:00.00,"
	start, stop = universe.split(",")[0:2]

	start = start.split("Start:")[-1].strip().split(".")[0]
	stop = stop.split("Stop:")[-1].strip().split(".")[0]

	# print(start)

	start_date_object = datetime.strptime(start, "%Y/%m/%d %H:%M:%S")
	# print(start_date_object)

	stop_date_object = datetime.strptime(stop, "%Y/%m/%d %H:%M:%S")
	# print(stop_date_object)

	# start_date, start_time = start.split(" ")
	# stop_date, stop_time = stop.split(" ")
	# print(start_date)
	# print(start_time)
	# print(stop)

def get_random_date():
	start_date = date(1800, 1, 1) 
	end_date = date(2024, 1, 1)

	total = end_date - start_date
	random_day = random.randrange(total.days)
	random_date = start_date + timedelta(days=random_day)	
	
	return random_date.year, random_date.month, random_date.day

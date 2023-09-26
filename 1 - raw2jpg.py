DEBUG = False

DIR = "/home/andrea/Documenti/personale/fotografie/"
M = "2023_09_2"
RAW_DIR = DIR+M+"/raw/"
JPG_DIR = DIR+M+"/jpg/"

import lib.gpxparser
punti = lib.gpxparser.getpoint (M)



import os
import PIL.Image
import PIL.ExifTags
from PIL import Image, ExifTags
from datetime import datetime, timedelta
import pytz
import lib.pyexiftool
from tqdm import tqdm

print("")
print("")
print("")

print ("###########################################")
print ("####### Estraggo metadati da CR2 ##########")
if DEBUG:
	print ("---2 File list:")
photo_file_list = []
for filename in os.listdir(RAW_DIR):
	if filename [-3:] != "xmp":
		photo_file_list.append(filename)

photo_list_data = []


for photo_file_name in tqdm(photo_file_list, desc ="Progress: "):
#for photo_file_name in photo_file_list:
	photo_data = {} # Photo name, datetimecreation corrette, datetimeGPS, lat, lon, ele
	photo_data['filename'] = photo_file_name
	if DEBUG:
		print ("     ", photo_data['filename'])
    
	img = PIL.Image.open(os.path.join(RAW_DIR, photo_file_name))
	exif_data = img.getexif()
	if DEBUG:
		if exif_data is None:
			print('Sorry, image has no exif data.')
		else:
			for key, val in exif_data.items():
				if key in ExifTags.TAGS:
					print(f'{ExifTags.TAGS[key]}:{val}')
	
	if exif_data:
		#creation_time = exif_data.get(306) # see https://exiv2.org/tags.html
		creation_time=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "CreateDate")
		datetime_creation = datetime.strptime(creation_time, '%Y:%m:%d %H:%M:%S')
		#print(datetime_creation)
		#Sintax: timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0) 
		datetime_creation = datetime_creation + timedelta(minutes=53)
		#print(datetime_creation)
		local = pytz.timezone("Europe/Rome")
		local_dt = local.localize(datetime_creation, is_dst=None)
		utc_dt = local_dt.astimezone(pytz.utc)
		photo_data['datetimecreation']=datetime_creation		
		#print(utc_dt)
		photo_data['Make']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "Make")
		photo_data['Camera_Model_Name']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "Model")
		photo_data['artist']="Andrea Alfieri"
		photo_data['Exposure_Time']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "ExposureTime")
		photo_data['F_Number']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "FNumber")
		photo_data['ISO']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "ISO")
		photo_data['Shutter_Speed_Value']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "ShutterSpeedValue")
		photo_data['Aperture_Value']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "ApertureValue")
		photo_data['Flash']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "Flash")
		photo_data['Focal_Length']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "FocalLength")
		photo_data['Lens_Type']=lib.pyexiftool.getExifData (RAW_DIR+"/"+photo_file_name, "LensType")
		
		min_diff = timedelta(minutes=5)
		point_time = 0
		for i in range (0, len(punti)):
			diff = abs(punti[i][0]-utc_dt)
			if diff<min_diff:
				min_diff = diff
				point_time = punti[i][0]
				lat = punti[i][1]
				lon = punti[i][2]
				ele = punti[i][3]
		if min_diff < timedelta(minutes=5):
			photo_data['pointtime']=point_time
			photo_data['lat']=lat
			photo_data['lon']=lon
			photo_data['ele']=ele
		photo_list_data.append(photo_data)

#print(photo_list_data)


import time
from geopy.geocoders import Nominatim

print ("")
print ("")
print ("")


print ("##########################")
print ("#### Start Geolocator ####")

geolocator = Nominatim(user_agent="a.alfieri@gmail.com")

num_elementi = len(photo_list_data)
i = 0
for i in tqdm(range(num_elementi), desc ="Progress: "):
	single_point = photo_list_data[i]
	time.sleep (1) # al massimo un interrogazione al secondo 
	if 'lat' in single_point:
		lat = single_point['lat']
		lon = single_point['lon']
		stringa = str(lat) + "," + str(lon)
		#print(stringa)
		location = geolocator.reverse(stringa)
		#print(location.raw)
		
		#print((location.latitude, location.longitude))
		comments = ""
		road = location.raw['address'].get('road',"")
		if road:
			comments = comments + road + " "
		village = location.raw['address'].get('village',"")
		if village:
			comments = comments + village + " "
		suburb = location.raw['address'].get('suburb',"")
		if suburb:
			comments = comments + suburb + " "
		town = location.raw['address'].get('town',"")
		if town:
			comments = comments + town + " "
		city = location.raw['address'].get('city',"")
		if city:
			comments = comments + city + " "	
		county = location.raw['address'].get('county',"")
		if county:
			comments = comments + county + " "	
		state = location.raw['address'].get('state',"")
		if state:
			comments = comments + state + " "	
		country = location.raw['address'].get('country',"")
		if country:
			comments = comments + country + " "	
		postcode = location.raw['address'].get('postcode',"")
		if postcode:
			comments = comments + postcode + " "	
		
		single_point['location']=comments
		single_point['Keywords']=comments
		single_point['City']=city + " " + town
		single_point['Sub-Location']=suburb + " " + village
		single_point['Province-State']=county + " " + state
		single_point['Country-PrimaryLocationName'] = country

#Keywords                        : Wolfe Tone Bridge, R336, Claddagh, Galway, County Galway, Irelan
#City                            : Claddagh, Galway
#Sub-location                    : Wolfe Tone Bridge, R336
#Province-State                  : County Galway
#Country-Primary Location Name   : Ireland


print ("##### End Geolocator #####")	
print ("##########################")


from GPSPhoto import gpsphoto

print ("###############################")
print ("#### Scrivo i tag su file  ####")

for obj in tqdm(photo_list_data, desc ="Convert to jpg: "):
#for obj in photo_list_data:
	jpeg_name = obj['filename'][:-4]+".jpg"
	if not(os.path.isfile(JPG_DIR+jpeg_name)):
		comando = "dcraw -v -w -c -q 3 -o 1 "+ RAW_DIR+obj['filename'] +" | cjpeg >"+ JPG_DIR+jpeg_name
		esecuzione = os.popen(comando)

for obj in tqdm(photo_list_data, desc ="Writing tags to jpg: "):
	jpeg_name = obj['filename'][:-4]+".jpg"
	if os.path.isfile(JPG_DIR+jpeg_name):	
		if 'lat' in obj:
			photo = gpsphoto.GPSPhoto(JPG_DIR+jpeg_name)
			info = gpsphoto.GPSInfo((obj['lat'], obj['lon']), int(obj['ele']), obj['pointtime'])
			# info = gpsphoto.GPSInfo((obj['lat'], obj['lon']))
			# Modify GPS Data
			photo.modGPSData(info, JPG_DIR+jpeg_name)
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "location", obj['location'])
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Keywords", obj['Keywords'])
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "City", obj['City'])
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Sub-Location", obj['Sub-Location'])
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Province-State", obj['Province-State'])
			lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Country-PrimaryLocationName", obj['Country-PrimaryLocationName'])
	
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "CreateDate", str(obj['datetimecreation']))
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "DateTimeOriginal", str(obj['datetimecreation']))
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "ModifyDate", str(obj['datetimecreation']))
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Make", obj['Make'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Model", obj['Camera_Model_Name'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "artist", obj['artist'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "ExposureTime", obj['Exposure_Time'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "FNumber", obj['F_Number'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "ISO", obj['ISO'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "ShutterSpeedValue", obj['Shutter_Speed_Value'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "ApertureValue", obj['Aperture_Value'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "Flash", obj['Flash'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "FocalLength", obj['Focal_Length'])
		lib.pyexiftool.setExifData (JPG_DIR+jpeg_name, "LensType", obj['Lens_Type'])



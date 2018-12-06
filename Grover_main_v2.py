#! /usr/bin/python

'''
Grover: a grain size-measuring rover using Pixhawk 2.0 connected via a serial connecti$

Developed by Grant Otto, Courtney Cowger, Zach El-Azom, Eriq Gloria, Cole Stinger, Aar$
University of Delaware Department of Mechanical Engineering
Faculty Advisor: Adam Wickenheiser

Developed for use at the Robotics Discovery Lab, University of Delaware School of Mari$
Sponsor and PI of Robotics Discovery Lab: Arthur Trembanis

wwww.udel.edu

All code is public and free to use.
'''

'''
***** KNOWN ISSUES *****
- take image function needs to add in all code for taking the image, gps point, stepper control, etc
- if the switch for the image capture is left down, the vehicle will continuously take image after image.
	In the future, the r/c channel will be changed to a button but this will require a bit more troubleshooting
	on the controller.

'''
import numpy as np
import cv2
import os
import sys
from pathlib import Path
import pyexiv2
import datetime
from dronekit import *
vehicle = connect('/dev/ttyS0', wait_ready=False, baud=921600)
#print("Hello, my name is Grover. The current firmware version is: ")
#print vehicle.version
print 'debug0'
print vehicle.system_status.state
print vehicle.armed
print vehicle.mode
print 'done checks'


#while True: 							# starts a perpetual loop any time the vehicle is connected
while vehicle.mode==VehicleMode('AUTO'): 		# if the vehicle is in auto
	print('debug1')
	print(vehicle.mode)		
	dist=distance_to_current_waypoint()
	while dist>1 and not dist == None:
		print('travelling to next waypoint...')
		time.sleep(1)	
	if dist<1 and not dist == None: 		# if the vehicle is less than a meter away from the current WP
		vehicle.mode = VehicleMode('HOLD') 	# put it on hold (on a rover, will stop the vehicle)
		time.sleep(3) 				# wait for the vehicle to come to a stop (3 seconds)
		#stepper down
		take_image()
		#stepper up
		#wipe lens
		vehicle.mode = VehicleMode('AUTO') 	# put it back in AUTO
		time.sleep(15) 				# wait for 15 seconds so the vehicle can exit
	elif dist==None:
		print('At Home')
		time.sleep(1)
while vehicle.mode==VehicleMode('MANUAL'): 		# if the vehicle is in MANUAL (remotely operated) mode:
	print('debug2')
	print(vehicle.mode)
	if rc.channel('6') > 1750: 			# if the switch by the H button on the Lightbridge is lowered
		vehicle.mode = VehicleMode('HOLD') 	# put the vehicle in HOLD (on a rover, will stop the vehicle)
		time.sleep(3) 				# wait for the vehicle to come to a stop
		take_image()
		vehicle.mode = VehicleMode('MANUAL')
							# ***make sure the switch is immediately put back up after turning down
while vehicle.mode==VehicleMode('HOLD'):
	print('holding')
	time.sleep(1)


def take_image():
	'''
	controls the stepper motor going down, the image being taken,
	and the stepper coming back up
	'''


	'''
	from whiteboard code:
	while switch = LOW
                lower stepper
        stop stepper
        retrieve gps point
        take usb image
        modify exif tag to include gps point
        save to directory
        raise stepper #may need a switch for the top of the stepper

	'''
	cap = cv2.VideoCapture(0) 							#zero is first webcam attatched
	filename = ''
	if cap.isOpened(): 								#checks if webcam is up and running
		ret, frame = cap.read() 						#capture single frame from the webcam to read
		#cv2.imshow('frame',frame)
	else:
		ret = False

	if ret:
		'''GPS Exif Tag Description: A pointer to the GPS Info IFD. The interoperability
		structure of the GPS Info IFD, like that of Exif IFD, has no image data
		Blah
		Need to install pyexiv package
		pyexiv2 is a module that allows your python scripts to read and write data
		embedded in image files
		'''
		#%m_%d_%Y - month_day_year
		#filename = "GrainImage_.png" #+ str(now) + ".png"
		filename = 'GrainImage_%s.png'%datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S') #writes filename with UTC date & time
		#path = 'C:/Users/Courtney/Documents/Github/Grover_control_scripts'
		#cv2.imwrite(os.path.join(path, filename), frame)
		print(filename) #sanity check to make sure filename is storing properly
		cv2.imwrite(filename, frame) #writes the frame to an image file
		#filename+=new_filename
		metadata = pyexiv2.ImageMetadata(filename) #calls for the metadata off of the image
		metadata.read() #reads the metadata
		metadata.modified = True
		metadata.writable = os.access(filename, os.W_OK)
		key = 'Exif.Image.ImageDescription' #reference for saving the gps data in the exif tag
		lat = (vehicle.location.global_frame.lat)
		lon = (vehicle.location.global_frame.lon)
		alt = (vehicle.location.global_frame.alt)
		value = '(%s, %s, %s)' %(lat,lon,alt) #takes the gps data from dronekit
		metadata[key] = pyexiv2.ExifTag(key, value) #writes the key and value to the exif tag
		metadata.write()

	cap.release() #relases the camera function

if __name__ == "__main__":
	take_image()


def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

distancetopoint=distance_to_current_waypoint()
print(distancetopoint)

def stepperdown():
	# tells the stepper to go down until it hits the switch
def stepperup():
	#tells the stepper to go back up
def wipe():
	#tells the servo to wipe the lens

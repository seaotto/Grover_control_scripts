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



import time
from dronekit import *
'''from dronekit import connect'''
vehicle = connect('/dev/ttyS0', wait_ready=True, baud=921600)
print("Hello, my name is Grover. The current firmware version is: ")
print vehicle.version


#main loop
while True: 							# starts a perpetual loop any time the vehicle is connected
	while vehicle.mode==VehicleMode('AUTO'): 		# if the vehicle is in auto
		dist=distance_to_current_waypoint()
		if dist<1 and not dist == None: 		# if the vehicle is less than a meter away from the current WP
			vehicle.mode = VehicleMode('HOLD') 	# put it on hold (on a rover, will stop the vehicle)
			time.sleep(3) 				# wait for the vehicle to come to a stop (3 seconds)
			print("take image")
			vehicle.mode = VehicleMode('AUTO') 	# put it back in AUTO
			time.sleep(15) 				# wait for 15 seconds so the vehicle can exit
	while vehicle.mode==VehicleMode('MANUAL'): 		# if the vehicle is in MANUAL (remotely operated) mode:
		if rc.channel('6') < 1750: 			# if the switch by the H button on the Lightbridge is lowered
			vehicle.mode = VehicleMode('HOLD') 	# put the vehicle in HOLD (on a rover, will stop the vehicle)
			print(vehicle.mode)
			time.sleep(3) 				# wait for the vehicle to come to a stop
			print("take image")
			vehicle.mode = VehicleMode('MANUAL')
								# ***make sure the switch is immediately put back up after turning down



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



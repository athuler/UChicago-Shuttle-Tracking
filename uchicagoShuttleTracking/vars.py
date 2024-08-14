from datetime import datetime, timezone
from geopy import distance
import pyproj
import yaml
import os

class Bus:
	
	def __init__(self, id):
		self.id = id
		self.route = None
		self.routeName = None
		self.pax = None
		self.paxBeforeArrival = None
		self.lat = None
		self.lon = None
		self.lastLat = None
		self.lastLon = None
		self.last_ping = None
		self.recentStop = None
		self.previousStop = None
		self.status = None
		self.timeArrivedAtStop = None
		self.atStop = None
		
	
	def ageSeconds(self):
		if(self.last_ping == None):
			return None
		
		return round((datetime.now(timezone.utc) - self.last_ping).total_seconds())
	
	def getClosestStop(
		self,
		detectionDistance = 30
	):
		
		if(
			# Exclude Undefined Buses
			self.route == None or
			
			# Exclude Buses W/O GPS
			self.lat == None or
			self.lon == None
		):
			return(None,None)
		
		# TODO: Instead of iterating through every stop in system, use "routes" to only iterate through stops for the current route
		
		# Get closest stop for current point
		for index, stop in busStops.items():
			if(self.route not in stop.routes and self.route != None):
				continue
			
			stopDistance = distance.distance(
					(self.lat, self.lon),
					(stop.lat, stop.lon)
				).m
			
			if(stopDistance <= detectionDistance):
				return(stop, stopDistance)
		
		
		if(
			# Exclude Buses with No Movement
			(self.lat == self.lastLat and
			self.lon == self.lastLon) or
			
			# Exclude No Previous Coordinates
			self.lastLat == None or
			self.lastLon == None
		):
			return(None, None)
		
		
		# Get closest stop along travel path
		geodesic = pyproj.Geod(ellps='WGS84')
		fwd_azimuth, back_azimuth, travelDist = geodesic.inv(
			self.lon,
			self.lat,
			self.lastLon,
			self.lastLat
		)
		midPoint = distance.distance(
				meters=int(travelDist/2)
			).destination(
				(self.lat, self.lon),
				bearing = back_azimuth
			)
		
		for index, stop in busStops.items():
			if(self.route not in stop.routes and self.route != None):
				continue
			
			stopDistance = distance.distance(
					(stop.lat, stop.lon),
					(midPoint.latitude, midPoint.longitude)
				).m
			
			if(stopDistance <= detectionDistance):
				#logs.append("Detected "+self.routeName+" From Midpoint At " + stop.name)
				return(stop, stopDistance)
		
		# No Stop Found
		return(None, None)
	
	def nextStop(self):
		if(
			self.route not in routes
			or 
			self.route == None
			or
			self.recentStop == None
		):
			return(None)
		
		nextStops = []
		
		for stop in routes[self.route].stops:
			if(stop.id != self.recentStop.id):
				continue
			
			nextStopIndex = routes[self.route].getStopIds().index(self.recentStop.id) + 1
			
			if(nextStopIndex >= len(routes[self.route].stops)):
				nextStopIndex = 0
				
			nextStops.append(routes[self.route].stops[nextStopIndex])
			
		return(nextStops)
			
	def recordStopEvent(self):
		logs.append(Log(f"recordStopEvent Triggered for {self.routeName} at {self.recentStop.name}"))
		
		paxLoad = self.pax - self.paxBeforeArrival
		if(paxLoad < 0):
			paxLoad = self.pax
		
		stopEvents.append(StopEvent(
			stop = self.recentStop,
			route = self.route,
			routeName = self.routeName,
			busId = self.id,
			arrivalTime = self.timeArrivedAtStop,
			departureTime = datetime.now(timezone.utc),
			passengerLoad = paxLoad,
			nextStop = self.nextStop()
		))
		
		return

class BusStop:
	
	def __init__(self, id, name, lat, lon):
		self.id = id
		self.name = name
		self.lat = lat
		self.lon = lon
		self.routes = []


class Route:
	def __init__(self, id, name = None, stops = []):
		self.id = id
		self.name = name
		self.stops = stops
	
	def getStopIds(self):
		stopIds = []
		for stop in self.stops:
			stopIds.append(stop.id)
		return(stopIds)


class StopEvent:
	def __init__(
		self,
		stop,
		route,
		routeName,
		busId,
		arrivalTime,
		departureTime,
		passengerLoad,
		nextStop
	):
		self.uploaded = False
		self.stop = stop
		self.route = route
		self.routeName = routeName
		self.busId = busId
		self.arrivalTime = arrivalTime
		self.departureTime = departureTime
		self.passengerLoad = passengerLoad
		self.nextStop = nextStop
		
		self.uiShown = False
		self.message = f"{self.routeName}\t{self.stop.name}\t{(self.departureTime-self.arrivalTime).seconds}s\t{self.passengerLoad}"

class Log:
	def __init__(self, message):
		self.message = message
		self.uiShown = False

class Error:
	def __init__(self, message):
		self.message = message
		self.uiShown = False

class LiveData:
	def __init__(self, message):
		self.message = message
		self.uiShown = False

def init(
	DB_HOST_,
	DB_NAME_,
	DB_USER_,
	DB_PASS_,
):

	# Load Config
	if not os.path.exists("config.yml"):
		open("config.yml", 'w').close()
	global config
	config = yaml.safe_load(open("config.yml"))
	if config is None:
		config = {}
	config["upload_data"] = True
	
	# Set Secrets
	global DB_HOST
	DB_HOST = DB_HOST_
	global DB_NAME
	DB_NAME = DB_NAME_
	global DB_USER
	DB_USER = DB_USER_
	global DB_PASS
	DB_PASS = DB_PASS_
	
	if config is None:
		config = {}
	
	global currentBuses
	currentBuses = {}
	
	global busStops
	busStops = {}
	
	global routes
	routes = {}
	
	global logs
	logs = []

	global recentMsgs
	recentMsgs = []
	
	global errors
	errors = []
	
	global systemAlerts
	systemAlerts = []
	
	global stopEvents
	stopEvents = []


class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

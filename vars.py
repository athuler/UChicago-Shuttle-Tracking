from datetime import datetime
from geopy import distance

class Bus:
	
	def __init__(self, id):
		self.id = id
		self.route = None
		self.routeName = None
		self.pax = None
		self.lat = None
		self.lon = None
		self.last_ping = None
	
	def ageSeconds(self):
		if(self.last_ping == None):
			return None
		
		return round((datetime.now() - self.last_ping).total_seconds())
	
	def getClosestStop(self):
		
		for index, stop in busStops.items():
			if(self.route not in stop.routes and self.route != None):
				continue
			
			stopDistance = distance.distance((self.lat, self.lon),(stop.lat, stop.lon)).m
			
			if(stopDistance <= 30):
				return(stop)
		return(None)
		

class BusStop:
	
	def __init__(self, id, name, lat, lon):
		self.id = id
		self.name = name
		self.lat = lat
		self.lon = lon
		self.routes = []

def init():
	
	global currentBuses
	currentBuses = {}
	
	global busStops
	busStops = {}
	
	global logs
	logs = []

	global recentMsgs
	recentMsgs = []
	
	global errors
	errors = []
	
	global systemAlerts
	systemAlerts = []


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

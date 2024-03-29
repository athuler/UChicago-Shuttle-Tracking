import requests
import websocket
import json
from dataHandling import *

BASE_URL = "https://passiogo.com"


def getAllRoutes(
	systemSelected = 1068,
	paramDigit = 1,
	amount = 1
):
	"""
	Obtains every route for the selected system.
	=========
	systemSelected: system from which to get content
	paramDigit: does not affect content of response, only formatting
	amount:
		1: Returns all routes for given system
		0: Not Valid, Gives Error
		>=2: Returns all routes for given system in addition to unrelated routes. Exact methodology unsure.
	"""
	
	
	# Initialize & Send Request
	url = BASE_URL+"/mapGetData.php?getRoutes="+str(paramDigit)
	body = {
			"systemSelected0" : str(systemSelected),
			"amount" : amount
			}
	response = requests.post(url, json = body)
	
	
	# Validate JSON Response
	try:
		routes = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	
	# Handle Differing Response Format
	if "all" in routes:
		routes = routes["all"]
	
	
	# Process Response
	print("Length:", len(routes))
	for route in routes:
		if "groupId" not in route:
			groupId = "None"
		else:
			groupId = route["groupId"]
		print(route["name"],"(",route["myid"],"/",groupId,")")
	
	return(routes)


def getAllStops(
	paramDigit = 2,
	systemSelected = 1068,
	sA = 1
):
	"""
	Obtains all stop for the selected system.
	=========
	systemSelected: system from which to get content
	paramDigit: No discernable change
	sA:
		0: error
		1: Returns all stops for the given system
		>=2: Returns unrelated stops as well
	"""
	
	
	# Initialize & Send Request
	url = BASE_URL+"/mapGetData.php?getStops="+str(paramDigit)
	body = {
			"s0" : str(systemSelected),
			"sA" : sA
			}
	response = requests.post(url, json = body)
	
	
	# Validate JSON Response
	try:
		stops = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	# Process Response
	print("Stops Length:",len(stops["stops"]))
	for index, stop in stops["stops"].items():
		#print(stop)
		print("#",stop["stopId"],"-",stop["name"],"- Route:", stop["routeName"],"(",stop["routeId"],") - Lat/Lon: (",stop["latitude"],"/",stop["longitude"],")")
	
	print("\n")
	print("Route Length:",len(stops["routes"]))
	for index, route in stops["routes"].items():
		print(route[0])
		for stopNum in range(2,len(route)):
			print("\tStop #",route[stopNum][0], "| id:", route[stopNum][1])
	
	return(stops)


def getSystemAlerts(
	paramDigit = 1,
	systemSelected = 1068
):
	"""
	Gets all system alerts for the selected system.
	=========
	systemSelected: system from which to get content
	paramDigit:
		0: Error
		>=1: Valid
	"""
	
	
	# Initialize & Send Request
	url = BASE_URL+"/goServices.php?getAlertMessages="+str(paramDigit)
	body = {
			"systemSelected0" : str(systemSelected),
			"amount" : 1,
			"routesAmount":0
			}
	response = requests.post(url, json = body)
	
	
	# Validate JSON Response
	try:
		errorMsg = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	
	# Process Response
	if(errorMsg["error"] != ""):
		print("Error:", errorMsg["error"])
	else:
		print("No Alerts!")
	
	for msg in errorMsg["msgs"]:
		print(msg)
	
	return(errorMsg)


def getBuses(
	paramDigit = 2,
	s0 = 1068
):
	"""
	Gets all currently running buses.
	=========
	s0: system from which to get content
	paramDigit:
		0: Error
		>=1: Valid
	"""
	
	
	# Initialize & Send Request
	url = BASE_URL+"/mapGetData.php?getBuses="+str(paramDigit)
	body = {
			"s0" : str(s0),
			"sA" : 1
			}
	response = requests.post(url, json = body)
	
	
	# Validate JSON Response
	try:
		buses = response.json()["buses"]
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	# Process Response
	for index,bus in buses.items():
		bus = bus[0]
		#print(bus,"\n")
		print("#", bus["busId"], bus["route"],"(",bus["routeId"],") - CalcCourse:",
			round(float(bus["calculatedCourse"]), 2),
			"Lat/Lon: (",bus["latitude"],"/",bus["longitude"],")"
		)
	return(buses)



# Launch WebSocket
def launchWS():
	uri = "wss://passio3.com/"
	#websocket.enableTrace(True) # For Debugging
	wsapp = websocket.WebSocketApp(
							uri,
							on_open = subscribeWS,
							on_message = handleNewWsMessage
			)
	print("Started WebSocket!")
	wsapp.run_forever()
	print("Connection Closed")
	launchWS()
	
	
	
def subscribeWS(wsapp):
	
	subscriptionMsg = {
		"subscribe":"location",
		"userId":[1068],
		#"filter":{"outOfService":0,"busId":[12642,12643,12645,12646,12647,12648,4313,4318,4320,4321,4322,4324,4331]},
		"field":["busId","latitude","longitude","course","paxLoad","more"]
	}
	print(json.dumps(subscriptionMsg))
	wsapp.send(json.dumps(subscriptionMsg))
	
	print("Subscribed!")


	
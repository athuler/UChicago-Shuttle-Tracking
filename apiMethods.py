import requests

BASE_URL = "https://passiogo.com"

# Get All Routes
def getAllRoutes(
	systemSelected = 1068,
	paramDigit = 1,
	deviceId = 43022372,
	amount = 1
):
	"""
	paramDigit: does not affect content of response, only formatting
	deviceId: does not affect response
	amount:
		1: Returns all routes for given system
		0: Not Valid, Gives Error
		>=2: Returns all routes for given system in addition to unrelated routes. Exact methodology unsure.
	"""
	url = BASE_URL+"/mapGetData.php?getRoutes="+str(paramDigit)+"&deviceId="+str(deviceId)
	body = {
			"systemSelected0" : str(systemSelected),
			"amount" : amount
			}

	response = requests.post(url, json = body)
	try:
		routes = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	if "all" in routes:
		routes = routes["all"]
	
	print("Length:", len(routes))

	for route in routes:
		if "groupId" not in route:
			groupId = "None"
		else:
			groupId = route["groupId"]
		
		
		print(route["name"],"(",route["myid"],"/",groupId,")")
	
	return(routes)


# Get All Stops
def getAllStops(
	paramDigit = 2,
	systemSelected = 1068,
	sA = 1
):
	"""
	paramDigit: No discernable change
	sA:
		0: error
		1: Returns all stops for the given system
		>=2: Returns unrelated stops as well
	"""
	
	url = BASE_URL+"/mapGetData.php?getStops="+str(paramDigit)
	body = {
			"s0" : str(systemSelected),
			"sA" : sA
			}

	response = requests.post(url, json = body)
	
	try:
		stops = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	print("Stops Length:",len(stops["stops"]))
	for index, stop in stops["stops"].items():
		print(stop["name"],"(" ,stop["stopId"],")", "\t\t Route:", stop["routeId"], "/", stop["routeName"])
		#print(index, stop,"\n")
	
	print("\n")
	print("Route Length:",len(stops["routes"]))
	for index, route in stops["routes"].items():
		#print(index, route,"\n")
		print(route[0])
		for stopNum in range(2,len(route)):
			print("\tStop #",route[stopNum][0], "| id:", route[stopNum][1])


# Get System Alerts
def getSystemAlerts(
	paramDigit = 1,
	systemSelected = 1068
):
	"""
	paramDigit:
		0: Error
		>=1: Valid
	"""
	url = BASE_URL+"/goServices.php?getAlertMessages="+str(paramDigit)
	body = {
			"systemSelected0" : str(systemSelected),
			"amount" : 1,
			"routesAmount":0
			}
	response = requests.post(url, json = body)
	
	
	try:
		errorMsg = response.json()
	except Exception as e:
		print("Response:", response.text)
		exit(e)
	
	print(errorMsg)
	return(errorMsg)
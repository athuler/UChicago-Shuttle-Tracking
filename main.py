# Load Libraries
import requests



# Get All Routes
def getAllRoutes():
	url = "https://passiogo.com/mapGetData.php?getRoutes=1&deviceId=43022372"
	body = {
			"systemSelected0" : "1068",
			"amount" : 1
			}

	response = requests.post(url, json = body)
	try:
		routes = response.json()
	except Exception as e:
		exit(str(e) + response.text)

	for route in routes:
		print(route)
	
	return routes

# Get All Stops
def getAllStops():
	url = "https://passiogo.com/mapGetData.php?getStops=2&deviceId=43022372&withOutdated=1&wBounds=1&buildNo=110&showBusInOos=0&lat=undefined&lng=undefined"
	body = {
			"s0" : "1068",
			"sA" : 1
			}

	response = requests.post(url, json = body)
	stops = response.json()
	#return stops
	
	for index, stop in stops["stops"].items():
		print(index, stop,"\n")

	for index, stop in stops["routes"].items():
		print(index, stop,"\n")


# Get System Alerts
def getSystemAlerts():
	url = "https://passiogo.com/goServices.php?getAlertMessages=1&deviceId=43022372&buildNo=110&embedded=0"
	body = {
			"systemSelected0" : "1068",
			"amount" : 1,
			"routesAmount":0
			}

	response = requests.post(url, json = body)
	print(response.json())
	
	
print("Getting All Routes")
getAllRoutes()
print("Getting All Stops")
getAllStops()
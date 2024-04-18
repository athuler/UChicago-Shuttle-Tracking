import json
import geopy.distance
import vars
from datetime import datetime


def handleNewWsMessage(wsapp, message):
	try:
		message = json.loads(str(message))
		
		
		
		# Handle Bus Data
		if(message["busId"] not in vars.currentBuses):
			vars.currentBuses[message["busId"]] = vars.Bus(message["busId"])
		
		# Update Passenger Load
		vars.currentBuses[message["busId"]].pax = message["paxLoad"]
		
		# Update Location
		vars.currentBuses[message["busId"]].lat = message["latitude"]
		vars.currentBuses[message["busId"]].lastLat = vars.currentBuses[message["busId"]].lat
		vars.currentBuses[message["busId"]].lon = message["longitude"]
		vars.currentBuses[message["busId"]].lastLon = vars.currentBuses[message["busId"]].lon
		
		# Update Ping
		vars.currentBuses[message["busId"]].last_ping = datetime.now()
		
		# Get Closest Stop
		try:
			closestStop, stopDistance = vars.currentBuses[message["busId"]].getClosestStop()
		except Exception as e:
			vars.errors.append("->Error Getting Closest Stop:" + str(e))
		
		if(closestStop != None):
			vars.currentBuses[message["busId"]].previousStop = vars.currentBuses[message["busId"]].recentStop
			vars.currentBuses[message["busId"]].recentStop = closestStop
			vars.currentBuses[message["busId"]].status = "At Stop"
			displayMsgStop = "Stop: " + str(closestStop.name)
		else:
			vars.currentBuses[message["busId"]].status = "Traveling"
			displayMsgStop = ""
			
		
		# Log New Data
		vars.recentMsgs.append(
			"#"+str(message["busId"])+"\t"+str(message["paxLoad"])+" pax\tLat/Lon: "+str(message["latitude"])+"/"+str(message["longitude"])+"\t"+displayMsgStop
		)
		
	except Exception as e:
		vars.errors.append("->MessageHandlingError:"+str(e))
	
	
	
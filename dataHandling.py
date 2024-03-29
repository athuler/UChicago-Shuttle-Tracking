import json
import geopy.distance
import vars


def handleNewWsMessage(wsapp, message):
	message = json.loads(str(message))
	#print("#", message["busId"], "-", message["paxLoad"],"pax - Lat/Lon", message["latitude"],"/", message["longitude"])
	vars.recentMsgs.append("#"+str(message["busId"])+"\t"+str(message["paxLoad"])+" pax\tLat/Lon: "+str(message["latitude"])+"/"+str(message["longitude"]))
	
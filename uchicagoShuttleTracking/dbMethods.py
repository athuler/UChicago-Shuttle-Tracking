import uchicagoShuttleTracking.vars as vars
from uchicagoShuttleTracking.secrets import *
import mysql.connector

def dbConnect():
	try:
		cnx = mysql.connector.connect(
			user = DB_USER,
			password = DB_PASS,
			host = DB_HOST,
			database = DB_NAME
		)
		vars.logs.append("Connected to DB")
		
		return(cnx)
		
	except Exception as e:
		vars.errors.append("->ErrorConnectingToDb: " + str(e))
		return None
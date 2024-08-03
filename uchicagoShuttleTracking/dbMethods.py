import uchicagoShuttleTracking.vars as vars
import mysql.connector

def dbConnect():
	try:
		cnx = mysql.connector.connect(
			user = vars.DB_USER,
			password = vars.DB_PASS,
			host = vars.DB_HOST,
			database = vars.DB_NAME
		)
		vars.logs.append("Connected to DB")
		
		return(cnx)
		
	except Exception as e:
		vars.errors.append("->ErrorConnectingToDb: " + str(e))
		return None
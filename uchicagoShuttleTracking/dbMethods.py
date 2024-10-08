import uchicagoShuttleTracking.vars as vars
import mysql.connector

def dbConnect():
	try:
		cnx = mysql.connector.connect(
			user = vars.DB_USER,
			password = vars.DB_PASS,
			host = vars.DB_HOST,
			database = vars.DB_NAME, 
			connection_timeout = 5
		)
		vars.logs.append(vars.Log("Connected to DB"))
		
		return(cnx)
		
	except Exception as e:
		vars.errors.append(vars.Error(f"->ErrorConnectingToDb: {e}"))
		vars.errors.append(vars.Error(f"User: {vars.DB_USER}, Host: {vars.DB_HOST}"))
		return None
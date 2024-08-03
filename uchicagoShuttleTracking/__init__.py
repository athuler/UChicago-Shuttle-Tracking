from uchicagoShuttleTracking.main import main
import threading
import subprocess
import sys
import time

global __version__
__version__ = "0.1.0"
PIP_URL = "git+https://github.com/athuler/UChicago-Shuttle-Tracking@main"


def run(
	quitOnUpdateAvailable = False,
	DB_HOST = "",
	DB_NAME = "",
	DB_USER = "",
	DB_PASS = "",
):
	
	return main(
		quitOnUpdateAvailable,
		__version__,
		DB_HOST,
		DB_NAME,
		DB_USER,
		DB_PASS,
		)
	

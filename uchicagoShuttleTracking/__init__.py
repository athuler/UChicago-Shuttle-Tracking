from uchicagoShuttleTracking.main import main
import threading
import subprocess
import sys
import time

global __version__
__version__ = "0.2.0"
PIP_URL = "git+https://github.com/athuler/UChicago-Shuttle-Tracking@main"


def run(
	quitOnUpdateAvailable = False,
	DB_HOST = None,
	DB_NAME = None,
	DB_USER = None,
	DB_PASS = None,
):
	
	return main(
			quitOnUpdateAvailable,
			__version__,
			PIP_URL,
			DB_HOST,
			DB_NAME,
			DB_USER,
			DB_PASS,
		)
	

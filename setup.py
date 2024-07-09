from setuptools import setup, find_packages
from uchicagoShuttleTracking import __version__

with open("README.md", 'r') as f:
	long_description = f.read()

setup(
	name='UChicago Shuttle Tracking',
	version=__version__,
	description="Tracking the Performance of UChicago's Shuttle Network",
	long_description=long_description,
	author='Andrei Thuler',
	author_email='info@andreithuler.com',
	url="https://github.com/athuler/UChicago-Shuttle-Tracking",
	packages=find_packages(),
	py_modules=find_packages(),
	install_requires=[
		"wheel",
	],
	
)
from setuptools import setup
import os
import shutil
import sys
import subprocess

if os.geteuid() != 0:
    print("This program must be run as root. Aborting.")
    sys.exit(1)

if os.environ['BOARD'] != 'Pynq-Z2':
    print("Only supported on a Pynq-Z2 Board")
    exit(1)

setup(
	name = "pynq_car",
	version = 1.0,
	url = 'https://github.com/xupsh/PYNQ-Car',
	license = 'BSD 3-Clause License',
	author = "Junhong Lin",
	author_email = "junhonghust@gmail.com",

	include_package_data = True,
	packages = ['pynqcar'],
	package_data = {
	'' : ['*.bit','*.tcl','*.py','*.bin','*.txt', '*.cpp', '*.h', '*.sh'],
	},
	description = "Robot Car Dvelopment Platform for PYNQ-Z2",
    install_requires=[
        'pynq','numpy'
    ],
)

if 'install' in sys.argv:
	if os.path.isdir(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-car/"):
		shutil.rmtree(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-car/")
	shutil.copytree("boards/Pynq-Z2/notebooks/",os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-car/")
	shutil.copytree("Robot/overlays/",os.path.join('/usr/local/lib',os.environ['PYNQ_PYTHON'],'dist-packages/pynq/overlays/')) #copy overlay
	shutil.copytree("Robot/lib/arduino/",os.path.join('/usr/local/lib',os.environ['PYNQ_PYTHON'],'dist-packages/pynq/lib/arduino/')) #copy overlay

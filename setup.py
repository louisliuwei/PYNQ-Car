from setuptools import setup, find_packages
import glob
import os
import subprocess
import sys
import shutil

board = os.environ['BOARD']
board_folder = 'boards/{}/'.format(board)

if os.geteuid() != 0:
    print("This program must be run as root. Aborting.")
    sys.exit(1)

if board != 'Pynq-Z2':
    print("Only supported on a Pynq-Z2 Board")
    exit(1)

setup(
	name = "pynq_car",
	version = 1.0,
	url = 'https://github.com/xupsh/PYNQ-Car',
	license = 'BSD 3-Clause License',
	author = "Junhong Lin",
	author_email = "junhonghust@gmail.com",

	packages = find_packages(),
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
	shutil.copytree("notebooks",os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-car/")

	if os.path.isdir(os.path.join('/usr/local/lib',os.environ['PYNQ_PYTHON'],'dist-packages/pynq/overlays/Robot')):
		shutil.rmtree(os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/overlays/Robot'))
	shutil.copytree(os.path.join(board_folder, 'overlays/Robot'), os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/overlays/Robot')) #copy overlay

	for f in os.listdir(os.path.join(board_folder, 'lib/arduino/')):
		shutil.copyfile(os.path.join(board_folder, 'lib/arduino/', f) ,os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/lib/arduino', f)) #copy lib

	if os.path.isdir(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/driver/"):
		shutil.rmtree(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/driver/")
	shutil.copytree(os.path.join(board_folder, 'driver'), os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/driver/") #copy driver

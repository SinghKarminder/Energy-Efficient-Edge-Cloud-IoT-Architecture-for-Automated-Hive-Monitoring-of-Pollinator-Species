#!/usr/bin/env python3

import requests
import paho.mqtt.client as mqtt
import os
import json
import ast
import time
import multiprocessing
path = "/etc/entomologist/"
with open(path + "ento.conf",'r') as file:
	data=json.load(file)
DEVICE_SERIAL_ID = data["device"]["SERIAL_ID"]
BUFFER_IMAGES_PATH = data["device"]["STORAGE_PATH"]


def upload_file(filename, response):

	try:
		with open(BUFFER_IMAGES_PATH+filename,'rb') as f:
			files = {'file': (filename,f)}
			http_resp = requests.post(response['url'], data=response['fields'], files = files)
		print(f"Uploaded file {filename} with response code {http_resp.status_code}")
	except:
		print(f"Could not upload file {filename}.")


def image_upload_manager():

	time.sleep(3)
	print("------------------ Starting Upload -------------------\n")

	with open("signedUrls.json","r") as f:
		payload_dict = ast.literal_eval(f.read())
		
	for files in payload_dict['files']:
		upload_file(files['filename'],files['url'])
		
	print("\n------------------ Upload Complete -------------------")
	
	

	

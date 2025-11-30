#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import datetime as dt
import subprocess
import random
import json
import sys
import socket
import ast
import time
import os
import multiprocessing
from sub import start_subscribe
from pub import start_publish
from imageUpload import image_upload_manager
from verification import start_verification
import logging as log
import glob
import csv


weather_path = "/media/mmcblk1p1/upload/weather*.csv"
device_stat_path = "/media/mmcblk1p1/upload/devicestats*.csv"


# Systemd notifier class
if sys.version_info < (3,):
    def _b(x):
        return x
else:
    import codecs
    def _b(x):
        return codecs.latin_1_encode(x)[0]

class SystemdNotifier:
    """This class holds a connection to the systemd notification socket
    and can be used to send messages to systemd using its notify method."""

    def __init__(self, debug=False):
        """Instantiate a new notifier object. This will initiate a connection
        to the systemd notification socket.
        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging.
        """
        self.debug = debug
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            addr = os.getenv('NOTIFY_SOCKET')
            if addr[0] == '@':
                addr = '\0' + addr[1:]
            self.socket.connect(addr)
        except Exception:
            self.socket = None
            if self.debug:
                raise

    def notify(self, state):
        """Send a notification to systemd. state is a string; see
        the man page of sd_notify (http://www.freedesktop.org/software/systemd/man/sd_notify.html)
        for a description of the allowable values.
        Normally this method silently ignores exceptions (for example, if the
        systemd notification socket is not available) to allow applications to
        function on non-systemd based systems. However, setting debug=True will
        cause this method to raise any exceptions generated to the caller, to
        aid in debugging."""
        try:
            self.socket.sendall(_b(state))
        except Exception:
            if self.debug:
                raise

# AWS Setup
log.basicConfig(filename='/var/tmp/cloud.log', filemode='w', level=log.INFO, format='[%(asctime)s]- %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')
with open(f"/etc/entomologist/ento.conf",'r') as file:
	data=json.load(file)


DEVICE_SERIAL_ID = data["device"]["SERIAL_ID"]
provisionstatus=data["device"]["PROVISION_STATUS"]


MQTT_BROKER = data["device"]["ENDPOINT_URL"]
PORT = 8883
MQTT_KEEP_INTERVAL = 44
rootCA = '/etc/entomologist/cert/AmazonRootCA1.pem'
cert = '/etc/entomologist/cert/certificate.pem.crt'
privateKey = '/etc/entomologist/cert/private.pem.key'

BUCKET_NAME = "test-entomologist-2"

# Publish Details

PUBLISH_CLIENT_NAME = f'{DEVICE_SERIAL_ID}_Publish_Client'
PUBLISH_TOPIC = f'cameraDevice/generateURL/{DEVICE_SERIAL_ID}'
PUBLISH_QoS = 1

#edit for job data upload
PUBLISH_CLIENT_JOB_LOG = f'{DEVICE_SERIAL_ID}_Client_Job_Log'
PUB_WEATHER = f'declient/{DEVICE_SERIAL_ID}/job/weather'
PUB_DEVICE = f'declient/{DEVICE_SERIAL_ID}/job/device'



# Subscribe Details

SUBSCRIBE_CLIENT_NAME = f'{DEVICE_SERIAL_ID}_Subscribe_Client'
SUBSCRIBE_TOPIC = f'cameraDevice/getURL/{DEVICE_SERIAL_ID}'
SUBSCRIBE_QoS = 0

# Verification Details
VERIFICATION_CLIENT_NAME = f'{DEVICE_SERIAL_ID}_Verification_Client'
VERIFICATION_TOPIC = f'cameraDevice/fileUploaded/{DEVICE_SERIAL_ID}'

# Buffer Storage Path

BUFFER_IMAGES_PATH = data["device"]["STORAGE_PATH"]


def generate_payload(filesList):



	payload = {
		"device-serialID":DEVICE_SERIAL_ID,
		"bucket-name":BUCKET_NAME,
		"files": filesList
	}

	return json.dumps(payload)

def signed_url_file_exist():
	log.info("Checking for signed URL json file exist")
	while "signedUrls.json" not in os.listdir():
		time.sleep(2)
	log.info("Signed Url file exist")
	return True


def upload_manager(filesList):

	batchSize = len(filesList)

	log.info("Generating for payload")
	publishPayload = generate_payload(filesList)
	log.info("Payload generated for upload")

	# Create start_subscribe and start_publish as two processes by implementing mulitprocessess.
	p1 = multiprocessing.Process(target = start_subscribe, args = [
		MQTT_BROKER,
		PORT,
		MQTT_KEEP_INTERVAL,
		SUBSCRIBE_CLIENT_NAME,
		SUBSCRIBE_TOPIC,
		SUBSCRIBE_QoS,
		rootCA,
		cert,
		privateKey])

	p2 = multiprocessing.Process(target = start_publish, args =[
		MQTT_BROKER,
		PORT,
		MQTT_KEEP_INTERVAL,
		PUBLISH_CLIENT_NAME,
		PUBLISH_TOPIC,
		PUBLISH_QoS,
		publishPayload,
		rootCA,
		cert,
		privateKey])
	p1.start()
	log.info("Start Subscribe process started")
	p2.start()
	log.info("Start Publish process started")
	p1.join()
	p2.join()
	log.info("Subscribe and publish process finished")

	# Create a better implementation once the signedUrls.json file has been created.
	if signed_url_file_exist():

		p3 = multiprocessing.Process(target = start_verification, args = [
		MQTT_BROKER,
		PORT,
		MQTT_KEEP_INTERVAL,
		VERIFICATION_CLIENT_NAME,
		VERIFICATION_TOPIC,
		SUBSCRIBE_QoS,
		batchSize,
		rootCA,
		cert,
		privateKey])

		p4 = multiprocessing.Process(target = image_upload_manager)

		p3.start()
		log.info("Start Verification process started")
		p4.start()
		log.info("Image Upload manager process started")
		p3.join()
		p4.join()
		log.info("Image Upload manager and verification process finished")

		os.remove('signedUrls.json')


def upload_job_data():
	#print("func: upload_job_data")
	client = mqtt.Client(PUBLISH_CLIENT_JOB_LOG)
	
	# setting tls certificates
	client.tls_set(rootCA, cert, privateKey)

	while True:
		try:
			client.connect(MQTT_BROKER, PORT, MQTT_KEEP_INTERVAL)
			break
		except:
			print("Did not connect")

	client.loop_start()

	
	weather_data = []
	device_stats = []
	#print("job:client connected")
	for filename in glob.glob(weather_path):
		file = open(filename, newline='')
		csv_reader = csv.reader(file)
		next(csv_reader)
		tmp_data = list(csv_reader)
		file.close()

		#appending list to weather data	
		weather_data.append(tmp_data)
		
	for filename in glob.glob(device_stat_path):
		file = open(filename, newline='')
		csv_reader = csv.reader(file)
		next(csv_reader)
		tmp_data = list(csv_reader)
		file.close()
			
		# appending new list to device_stats file
		device_stats.append(tmp_data)

	json_payload_weather = {"serial_ID": DEVICE_SERIAL_ID, "weather_data": weather_data}
	json_payload_device = {"serial_ID": DEVICE_SERIAL_ID,  "device_stats": device_stats}

	#data publish
	client.publish(PUB_WEATHER, json.dumps(json_payload_weather),1)
	client.publish(PUB_DEVICE, json.dumps(json_payload_device),1)
	
	#print(json_payload_weather)	

	#print("job:publish")
	client.loop_stop()
	client.disconnect()
		


def main():
	log.info("Cloud Main started..")
	n = SystemdNotifier()
	while True:
		if provisionstatus=="True":
			if len(glob.glob(weather_path)):
				#print("calling: upload_job")
				upload_job_data()
			while len(os.listdir(BUFFER_IMAGES_PATH)):
				filesList = os.listdir(BUFFER_IMAGES_PATH)[:10]
				n.notify("WATCHDOG=1")
				log.info("Calling upload manager..")
				upload_manager(filesList)
				log.info("Upload manager successfully executed..")
			log.info("-"*50)
			time.sleep(1)
		else:
			log.info("I m running but provison status is False")
			time.sleep(10)



main()

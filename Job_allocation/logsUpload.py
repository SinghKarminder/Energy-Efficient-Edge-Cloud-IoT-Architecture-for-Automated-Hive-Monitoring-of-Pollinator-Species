#!/usr/bin/env python3

import requests
import os
import json

with open("/etc/entomologist/ento.conf","r") as file:
  data = json.load(file)

bucket_name = data["device"]["IP_BUCKET"]

log_file_path = '/var/tmp/'

def upload_log_file():
  log_files = os.listdir(log_file_path)
  for filename in log_files:
    url=f"https://w19bo3qwde.execute-api.us-east-1.amazonaws.com/v1/{bucket_name}/{filename}"
    try:
			
      http_resp = requests.put(url, data = open(log_file_path+filename))
      print(f"Uploaded file with response code {http_resp.status_code}")
    except Exception as e:
      print(e)

	

	

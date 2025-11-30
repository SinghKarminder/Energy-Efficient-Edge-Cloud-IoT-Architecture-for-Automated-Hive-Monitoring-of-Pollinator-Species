#!/usr/bin/env python3

from re import sub
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import requests
import time
import json
import threading
import logging as log
import subprocess
import cv2
#from logsUpload import upload_log_file

#log.basicConfig(filename='/var/tmp/job.log', filemode='w', level=log.INFO, format='[%(asctime)s]- %(message)s', datefmt='%d-%m-%Y %I:%M:%S %p')

now=datetime.now()
time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")


# read ento.conf file
with open("/etc/entomologist/ento.conf","r") as f:
    config_data = json.load(f)

# cloud configuration
device_id = config_data["device"]["SERIAL_ID"]
SERIAL_ID=device_id
mqttBroker = config_data["device"]["ENDPOINT_URL"]
mqtt_client = "device_manager/"+ device_id
client = mqtt.Client(mqtt_client)
port = 8883

# publish topics
t_pub_data = f"declient/{SERIAL_ID}/data/resp"
t_pub_config = f"declient/{SERIAL_ID}/config/resp"
t_pub_image = f"declient/{SERIAL_ID}/image/resp"
t_pub_job = f"declient/{SERIAL_ID}/job/resp"

#topic_pub_devicestats = "device_manager/devicestats/" + device_id
#topic_sub_config = "device_manager/config/" + device_id


# subscribe topics
t_sub_job = f"cameraDevice/job/{SERIAL_ID}"
t_sub_data = f"declient/{SERIAL_ID}/data/req"
t_sub_config = f"declient/{SERIAL_ID}/config/req"
t_sub_image = f"declient/{SERIAL_ID}/image/req"

path = "/etc/entomologist/"

# multiple subscribe
SUB_TOPIC = [(t_sub_job,0),(t_sub_data,0),(t_sub_config,0),(t_sub_image,0)]

# #DE board certificate path
rootCA="/etc/entomologist/cert/AmazonRootCA1.pem"
cert="/etc/entomologist/cert/certificate.pem.crt"
key="/etc/entomologist/cert/private.pem.key"


client.tls_set(rootCA,cert,key)

MQTT_KEEPALIVE_INTERVAL = 45

def publish_data(client, topic, qos, payload):
    client.publish(topic, payload, qos)

def readfile(filename):
    data={}
    try:
        with open(filename,'r') as file:
            data=json.load(file)
    except FileNotFoundError:
        data={"error":"FileNotFoundError"}
    except json.decoder.JSONDecodeError:
        data={"Error":"File is passed instead of json file"}
    except Exception as e:
        data={"error":str(e)}
    return data



# read rana application configuration file
def readRanaConfigData():
    temp={}
    with open("/usr/sbin/rana/ranacore.conf",'r') as file:
        data=file.readlines()
        for line in data:
            if line[0]!='#' and line[0]!='\n':
                ind=line.index(" ")
                val_index=line.index("\n")
                key=line[:ind]
                value=line[ind+1:val_index]
                # temp.append([key,value])
                temp[key] = value
    return temp

# read camera controls
def read_camera_control():
    data={}
    try:
        var = subprocess.check_output("v4l2-ctl --device /dev/video2 --list-ctrls".split())
        output = var.decode('utf-8')
        output = output.split('\n')
        for index in range(len(output)-1):
            output[index] = output[index].strip()
            temp = output[index].split()
            if '(int)' in temp:
                data[temp[0]]=[]
                data[temp[0]].append(temp[4].split('=')[-1])
                data[temp[0]].append(temp[5].split('=')[-1])
                data[temp[0]].append(temp[6].split('=')[-1])
                data[temp[0]].append(temp[7].split('=')[-1])
                data[temp[0]].append(temp[8].split('=')[-1])
    except:
        data["error"]="Something is wrong on v4l2"
    return data

def get_camera_control():
    return readfile("/etc/entomologist/camera_control.conf")

# devicestats
def devicestats():
    payload = {
            "DeviceID": device_id,
            "mac": readfile("/tmp/network_address")["mac"],
            "ip": readfile("/tmp/network_address")["ip"],
            "time": f"{datetime.now()}",
            "devicestats": readfile("/tmp/devicestats"),
            "gps": readfile("/tmp/gps")
    }
    return json.dumps(payload)


def image_payload(client,data,status):
    payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : status,
        "value": {}
    }
    client.publish(t_pub_image, json.dumps(payload), 0)


def rana_payload(client,data):
    payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : "success",
        "value": readRanaConfigData()
    }
    client.publish(t_pub_data, json.dumps(payload), 0)


def camera_payload(client,data):
    payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : "success",
        "value":  get_camera_control()
        }
    client.publish(t_pub_data, json.dumps(payload), 0)

def device_payload(client,data):
    subprocess.call(["/usr/sbin/device-manager/DeviceManager/job_data.sh"])
    subprocess.call(["/usr/sbin/device-manager/DeviceManager/storage_state.sh"])
    subprocess.call(["/usr/sbin/device-manager/DeviceManager/cellular.sh"])
    subprocess.call(["/usr/sbin/jobreceiver/nif_up.sh"])
    #call for modem data
    subprocess.call(["/usr/sbin/jobreceiver/data_usage.sh"])


    payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : "sucess",
        "value": {
            "mac": readfile("/tmp/network_address")["mac"],
            "ip": readfile("/tmp/network_address")["ip"],
            "devicestats": readfile("/tmp/devicestats"),
            "gps": readfile("/tmp/gps"),
            "storage": readfile("/tmp/storage"),
            "cellular": readfile("/tmp/cellular"),
            "job": readfile("/tmp/job"),
            "modem": readfile("/tmp/modem")
            }
        }
    client.publish(t_pub_data, json.dumps(payload), 0)


def upload_image(client,url):
        #print(url)
        while os.path.exists('/tmp/rana_active'):
            time.sleep(0.05)
        camera = cv2.VideoCapture(2)  # use 0 for web camera
        camera.set(cv2.CAP_PROP_FPS,60)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        success, frame = camera.read()  # read the camera frame
        cv2.imwrite('/usr/sbin/jobreceiver/test_image.jpeg',frame)
        camera.release()
        #subprocess.call("/usr/sbin/jobreceiver/image_capture.sh")
        with open("/usr/sbin/jobreceiver/test_image.jpeg",'rb') as f:
                files = {'file': (url['fields']['key'],f)}
                http_resp = requests.post(url['url'], data=url['fields'], files = files)
                resp_code = http_resp.status_code
                print(resp_code)
        if resp_code == 204:
            payload = image_payload(client,url,"success")
        else:
            payload = image_payload(client,url,"fail")

def data_handler(client,data):
    if data['category'] == "device":
        device_payload(client,data)
   
    if data['category'] == "rana":
        rana_payload(client,data)

    if data['category'] == "camera":
        camera_payload(client,data)

# update camera controls
def update_cam_ctrl(keyValue):
        data={}
        path="/etc/entomologist/"
        with open(path + "camera_control.conf",'r') as file:
            data=json.load(file)
        with open(path + "camera_control.conf",'w') as file:
            data.update(keyValue)
            #data.update({name:dataa})
            json.dump(data,file,indent=4,separators=(',', ': '))



def config_rana(data):
        contentDict={}
        content=None
        #print("rana config")
        #print(data['value']['image_overlays'])
        with open("/usr/sbin/rana/ranacore.conf",'r') as file:
            content=file.readlines()
        count=0
        for line in content:
            if line[0]!='#' and line[0]!='\n':
                ind=line.index(" ")
                key=line[:ind]
                value=data['value'][key]
                #print(value)
                contentDict[key]=(value,count)
            count+=1
        for key in contentDict:
            line=key+" "+contentDict[key][0]+'\n'
            content[contentDict[key][1]]=line
        with open("/usr/sbin/rana/ranacore.conf",'w') as file:
            file.writelines(content)
        #return redirect(url_for('configurations'))
        payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : "success",
        "value": {}
        }
        client.publish(t_pub_config, json.dumps(payload), 0)



def config_camera(client,data):
    for (key, value) in data['value'].items():
    
    #print(data['value'])
        subprocess.call(f"v4l2-ctl --device /dev/video2 --set-ctrl={key}={value}".split())
        update_cam_ctrl({key:value})
    payload = {
        "device_id": SERIAL_ID,
        "ts": f"{datetime.now()}",
        "request_id": data['request_id'],
        "user": data['user'],
        "category": data['category'],
        "status" : "success",
        "value": {}
    }
    client.publish(t_pub_config, json.dumps(payload), 0)


def config_request(client,data):
    if data['category'] == "rana":
        config_rana(data)

    if data['category'] == "camera":
        config_camera(client,data)


def updateData(name,keyValue):
#        print(updateData)
        data={}
        with open(path + "ento.conf",'r') as file:
            data=json.load(file)
            dataa=data[name]
        with open(path + "ento.conf",'w') as file:
            dataa.update(keyValue)
            data.update({name:dataa})
            json.dump(data,file,indent=4,separators=(',', ': '))


def parse(jobconfig,client):
#        print(parse)
        try:
                if jobconfig['deviceId'] == SERIAL_ID:
                        if 'Device-Test-Flag' in jobconfig['device'] and jobconfig['device']['Device-Test-Flag']=='True':
                                updateData("device",{"TEST_FLAG":"True"})
                                testDuration = jobconfig['device']['Device-Test-Duration']
                                updateData("device",{"TEST_DURATION":testDuration})

                        if 'Device-On-Time' in jobconfig['device']:
                                onTime=jobconfig['device']['Device-On-Time']
                                updateData("device",{"ON_TIME":onTime})

                        if 'Device-Off-Time' in jobconfig['device']:
                                offTime=jobconfig['device']['Device-Off-Time']
                                updateData("device",{"OFF_TIME":offTime})

                        if 'jobId' in jobconfig:
                                job_id=jobconfig['jobId']
                                updateData("device",{"JOB_ID":job_id})
                        
                        timeZone=" "
                        if 'Time-Zone' in jobconfig['device']:
                                timeZone=jobconfig['device']['Time-Zone']
                                updateData("device",{"Time-Zone":timeZone})
                                subprocess.run(['timedatectl','set-timezone',timeZone])

                        if 'Get-All-Logs' in jobconfig['getLogs']:
                                log_thread = threading.Thread(name='upload_log_file', target = upload_log_file)
                                log_thread.start()

                        log.info("JOB RECIEVED and PARSED Successfully..")

                        # acknowledment for job
                        payload = {
                            "device_id": jobconfig['deviceId'],
                            "ts": f"{datetime.now()}",
                            "request_id": 245,
                            "user": "milan",
                            "category": "job",
                            "status" : "success",
                            "value": {
                                "TimeZone": timeZone,
                                "DeviceOnTime": jobconfig['device']['Device-On-Time'],
                                "DeviceOffTime": jobconfig['device']['Device-Off-Time'],
                                "jobId": jobconfig['jobId']
                              }
                        }
                        client.publish(t_pub_job, json.dumps(payload), 0)

        except:
                log.info("Tried to parsed and failed..")


# Callback Functions
def on_log(client, userdata, level, buf):
	print("Log: "+buf)

# callback function for connect
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker") 
        # subscribe with qos 1
        #client.subscribe(topic_sub_config,1)
        client.subscribe(SUB_TOPIC)
        print("sucessfully subscribed")
    else:
        Connected = False
        print("Connection failed")

# callback for message arrived
def on_message_config(client, userdata, message):
    conf_data = json.loads(message.payload.decode('utf-8'))
    t_conf = threading.Thread(target=config_request ,args=(client,conf_data))
    t_conf.start()

def on_message_image(client, userdata, message):
    url = json.loads(message.payload.decode('utf-8'))
    t_image = threading.Thread(target=upload_image, args=(client, url))
    t_image.start()


def on_message_data(client, userdata, message):
    #print(f"msg arrvd on topic {message.topic}")
    data = json.loads(message.payload.decode('utf-8'))
    t_data = threading.Thread(target=data_handler, args=(client, data))
    t_data.start()


def on_message_job(client, userdata, message):
    print("msg arrvd")
    jobconfig = json.loads(message.payload.decode('utf-8'))
    t_job = threading.Thread(name='parse', target=parse,args=(jobconfig,client))
    t_job.start()



# set callbacks
client.on_connect = on_connect
#client.on_message = on_message
client.message_callback_add(t_sub_job, on_message_job)
client.message_callback_add(t_sub_data, on_message_data)
client.message_callback_add(t_sub_config, on_message_config)
client.message_callback_add(t_sub_image, on_message_image)


# trying to connect
try:
    client.connect(mqttBroker, port, MQTT_KEEPALIVE_INTERVAL)
except:
    print("Did not connect")

client.loop_forever()

#try:
#    while True:
#        publish_data(client,topic_pub_devicestats,0)

#except KeyboardInterrupt:
#    print("keyboard interrupt\n")
#    client.disconnect()
#    client.loop_stop()


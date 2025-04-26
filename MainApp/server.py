import base64
import json
import cv2
import numpy as np
from kafka import KafkaConsumer
from paho.mqtt import client as mqtt
from ultralytics import YOLO
import config  
import time

# ThingsBoard config
THINGSBOARD_TOKEN = 'BqlbHOO9sXWI0hmTotYY'
THINGSBOARD_HOST = "mqtt.thingsboard.cloud"
THINGSBOARD_PORT = 1883
MQTT_TOPIC = "v1/devices/me/telemetry"

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(THINGSBOARD_TOKEN)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT connected to ThingsBoard!")
        else:
            print(f"MQTT connection failed: {rc}")
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)

# Load YOLOv11 model
model = YOLO("Model/yolo11s.pt") 

# Kafka setup
consumer = KafkaConsumer(
    "receive_result",
    bootstrap_servers=[config.kafka_ip],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    security_protocol="SSL",
    ssl_cafile="root.crt",      
    ssl_certfile=None,                 
    ssl_keyfile=None,  
    fetch_max_bytes=9000000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# Connect MQTT
connect_mqtt()
mqtt_client.loop_start()

print("Server started. Waiting for images from Kafka...")

for msg in consumer:
    data = msg.value
    room_id = data["RoomID"]
    image_b64 = data["image"]

    # Decode base64 -> image
    img_bytes = base64.b64decode(image_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Detect people
    results = model(frame)
    people_count = 0
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            # 0 is class 'person' in COCO
            if cls_id == 0:
                people_count += 1

    # Push result on ThingsBoard
    telemetry_data = {
        "room_id": room_id,
        "people_count": people_count,
        "timestamp": int(time.time())
    }
    print(telemetry_data)

    mqtt_client.publish(MQTT_TOPIC, json.dumps(telemetry_data))
    print(f"Room {room_id}: {people_count} people detected → published to ThingsBoard.")


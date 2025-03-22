import time
import requests
import base64
from kafka import KafkaProducer,KafkaConsumer
import cv2
import json
import threading

from picamera2 import Picamera2, Preview

kafka_ip = " 192.168.43.188:9092"

topic_name_consumer = "send_result"
c = KafkaConsumer(
    topic_name_consumer,
    bootstrap_servers = [kafka_ip],
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    fetch_max_bytes = 9000000,
    fetch_max_wait_ms = 10000,
)

topic_name_producer = "receive_result"
p = KafkaProducer(
    bootstrap_servers=[kafka_ip],
    max_request_size = 9000000,
)

picam = Picamera2()

config = picam.create_preview_configuration()
picam.configure(config)

picam.start_preview(Preview.QTGL)

picam.start()
time.sleep(5)
picam.capture_file("result.jpg")

picam.close()

# Function to encode image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

# Server url

image_path = 'result.jpg'
encoded_image_data = encode_image_to_base64(image_path)

def producer_thread():
    data = {
        'image': encoded_image_data,
        'RoomID' : "E2",
        'w': 160,  #  width
        'h': 160   #  height
    }
    json_data = json.dumps(data).encode('utf-8')
    p.send(topic_name_producer, json_data)
    print("Image Sent!")

def consumer_thread():
    try:
         for message in c:
            stream = message.value
            data = json.loads(stream)
            result = data['name']
            result_id = data['room']
            if result is not None and result_id is not None:
                print("Student: ", result)
                print("Room: ", result_id)
                exit()
            else:
                print("Warning: Invalid data received. Missing 'name' or 'room' key.")
    finally:
        c.close()  

producer_t = threading.Thread(target=producer_thread)
consumer_t = threading.Thread(target=consumer_thread)

producer_t.start()
consumer_t.start()

producer_t.join()
consumer_t.join()

import time
import requests
import base64
from kafka import KafkaProducer, KafkaConsumer
import cv2
import json
import threading
from picamera2 import Picamera2, Preview

kafka_ip = "192.168.43.58:9093"

topic_name_producer = "TEST"
topic_name_receive = "SEND"

c = KafkaConsumer(
    topic_name_receive,
    bootstrap_servers=[kafka_ip],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    security_protocol="SSL",
    ssl_cafile="root.crt",      
    ssl_certfile="server.crt",                 
    ssl_keyfile="server.key",  
    fetch_max_bytes=9000000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)
p = KafkaProducer(
    bootstrap_servers=[kafka_ip],
    security_protocol="SSL",
    ssl_cafile="root.crt",  
    ssl_certfile="client.crt",
    ssl_keyfile="client.key",
    max_request_size=9000000,
)
picam = Picamera2()

# Set up camera preview and configuration
config = picam.create_preview_configuration()
picam.configure(config)
picam.start_preview(Preview.QTGL)

picam.start()

# Function to encode image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

# Function to capture an image and send it to Kafka
def capture_and_send_image():
    while True:
        image_path = "result.jpg"
        picam.capture_file(image_path)

        encoded_image_data = encode_image_to_base64(image_path)

        # Prepare data to send via Kafka
        data = {
            'image': encoded_image_data,
            'RoomID': "E2",
            'w': 160,  # width
            'h': 160   # height
        }

        json_data = json.dumps(data).encode('utf-8')

        # Send the image data to Kafka
        p.send(topic_name_producer, json_data)
        print("Image Sent!")

        # Sleep for 5 seconds before capturing the next image
        time.sleep(5)

# Function to consume messages from Kafka
def consumer_thread():
    for message in c:
        data = message.value
        room = data['room_id']
        count = data['people_count']
        date =  data['timestamp']

        if room is not None and count is not None:
            print("Student: ", room)
            print("Room: ", count)
            print("Date:", date)
        else:
            print("Warning: Invalid data received.")

# Start producer and consumer threads
producer_t = threading.Thread(target=capture_and_send_image)
consumer_t = threading.Thread(target=consumer_thread)

producer_t.start()
consumer_t.start()

producer_t.join()
consumer_t.join()

# Stop the preview and close the camera
picam.close()

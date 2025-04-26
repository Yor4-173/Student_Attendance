import time
import base64
from kafka import KafkaProducer, KafkaConsumer
import cv2
import json
import threading

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
    ssl_certfile=None,                 
    ssl_keyfile=None,  
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

# Function to encode image to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

# Function to send an image repeatedly
def capture_and_send_image():
    while True:
        image_path = "result.jpg"
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
        time.sleep(10)

# Function to consume messages from Kafka
def consumer_thread():
    try:
        for message in c:
            stream = message.value
            data = json.loads(stream)
            room = data['room_id']
            count = data['people_count']
            date =  data['timestamp']

            if room is not None and count is not None:
                print("Student: ", room)
                print("Room: ", count)
                print("Date:", date)
                exit()
            else:
                print("Warning: Invalid data received.")
    finally:
        c.close()

# Start producer and consumer threads
producer_t = threading.Thread(target=capture_and_send_image)
consumer_t = threading.Thread(target=consumer_thread)

producer_t.start()
consumer_t.start()

producer_t.join()
consumer_t.join()

import time
import base64
from kafka import KafkaProducer
import cv2
import json

kafka_ip = "192.168.43.58:9093"

topic_name_producer = "TEST"
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
def send_image_loop():
    image_path = "result.jpg"  

    while True:
        frame = cv2.imread(image_path)

        if frame is None:
            print(f"Cannot read image at {image_path}")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        encoded_image_data = base64.b64encode(buffer).decode('utf-8')
        data = {
            'image': encoded_image_data,
            'RoomID': "E2",
            'w': frame.shape[1],  # width
            'h': frame.shape[0]   # height
        }

        json_data = json.dumps(data).encode('utf-8')

        # Send Kafka
        p.send(topic_name_producer, json_data)
        print("Image Sent!")

        if cv2.waitKey(10000) & 0xFF == ord('q'):
            print("Exit signal received. Shutting down...")
            break

    cv2.destroyAllWindows()

send_image_loop()

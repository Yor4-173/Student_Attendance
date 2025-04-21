
import base64
from kafka import KafkaProducer,KafkaConsumer
import config
import time
import cv2
import json
import threading

topic_name_consumer = "send_result"
c = KafkaConsumer(
    topic_name_consumer,
    bootstrap_servers = [config.kafka_ip],
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    fetch_max_bytes = 9000000,
    fetch_max_wait_ms = 10000,
)

topic_name_producer = "receive_result"
p = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    max_request_size = 9000000,
)

def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return encoded_image

def producer_thread():
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if ret:
            frame = cv2.resize(frame, dsize=(160, 160))
            encoded_image_data = encode_image_to_base64(frame)
            data = {
                'image': encoded_image_data,
                'RoomID' : "E1",
                'w': 160,  # width
                'h': 160   # height
            }
            json_data = json.dumps(data).encode('utf-8')
            p.send(topic_name_producer, json_data)
            print("Image Sent!")
            time.sleep(5)
            cv2.waitKey(1)
            break
        else:
            print("Error: Could not read frame from camera.")
            break
    cam.release()

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



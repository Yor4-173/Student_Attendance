import cv2
from kafka import KafkaProducer
import config
import time

topic_name = "send_result"
p = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    max_request_size = 9000000,
)
cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    if ret:
        frame = cv2.resize (frame, dsize=None, fx=0.2, fy=0.2)
        ret, buffer = cv2.imencode('.jpg', frame)
        p.send(topic_name, buffer.tobytes())
        p.flush()
        print("Sent!")
        time.sleep(60)
    cv2.waitKey(1)
cam.release()
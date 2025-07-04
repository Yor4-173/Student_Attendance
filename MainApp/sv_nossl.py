import base64
import json
import cv2
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from ultralytics import YOLO
import config  
import time

# Load YOLOv11 model
model = YOLO("Model/yolo11s.pt") 
# receive_topic = "receive_result"
receive_topic = "RASP_SEND"
# Topic to send results
send_topic = "RASP_RECEIVE"

# Kafka setup
consumer = KafkaConsumer(
    receive_topic,
    bootstrap_servers=[config.kafka_ip],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    fetch_max_bytes=9000000,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)
producer = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    max_request_size = 9000000,
)   



print("Server started. Waiting for images from Kafka...")

while True:
    for msg in consumer:
        data = msg.value
        room_id = data["RoomID"]
        image_b64 = data["image"]

        # Decode base64 -> image
        img_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Detect people
        results = model(frame, verbose=False)
        people_count = 0
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                # 0 is class 'person' in COCO
                if cls_id == 0:
                    people_count += 1

        telemetry_data = {
            "room_id": room_id,
            "people_count": people_count,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }
        producer.send(send_topic, json.dumps(telemetry_data).encode('utf-8'))
        print("Result sended!")
        producer.flush()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Room {room_id}: {people_count} people detected.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exit signal received. Shutting down...")
        break

cv2.destroyAllWindows()
consumer.close()

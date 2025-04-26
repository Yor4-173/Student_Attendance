import base64
import json
import cv2
import numpy as np
from kafka import KafkaConsumer
from ultralytics import YOLO
import config  
import time

# Load YOLOv11 model
model = YOLO("Model/yolo11s.pt") 
# receive_topic = "receive_result"
receive_topic = "TEST"

# Kafka setup
consumer = KafkaConsumer(
    receive_topic,
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
    results = model(frame, verbose=False)
    people_count = 0
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            # 0 is class 'person' in COCO
            if cls_id == 0:
                people_count += 1

    # In kết quả ra console
    telemetry_data = {
        "room_id": room_id,
        "people_count": people_count,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    }
    print(telemetry_data)

    print(f"Room {room_id}: {people_count} people detected.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exit signal received. Shutting down...")
        break

cv2.destroyAllWindows()
consumer.close()

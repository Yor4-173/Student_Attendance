import cv2
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import config
topic_name = "send_result"
c = KafkaConsumer(
    topic_name,
    bootstrap_servers = [config.kafka_ip],
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    fetch_max_bytes = 9000000,
    fetch_max_wait_ms = 10000,
)

topic_name_out = "receive_result"
p = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    max_request_size = 9000000,
)

for message in c:
    stream = message.value
    stream = np.frombuffer(stream, dtype=np.uint8)
    image = cv2.imdecode(stream, cv2.IMREAD_COLOR)
    print("Recognizing")
    cv2.putText(image, "PROCESSED", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imwrite("PROCESSED.png", image)
    ret, buffer = cv2.imencode('.jpg', image)
    print("Done!")
    p.send(topic_name_out, buffer.tobytes())
    p.flush()


import json
import config
from kafka import KafkaProducer

topic_name = "TEST"

p = KafkaProducer(
    bootstrap_servers = [config.kafka_ip],
    security_protocol="SSL",
    ssl_cafile="root.crt",  
    ssl_certfile="client.crt",
    ssl_keyfile="client.key",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

p.send(topic_name, {"Name": "Alice"})
p.flush()

print("Sent")
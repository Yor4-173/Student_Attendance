import json
from kafka import KafkaConsumer
import config

topic_name = "TEST"

c = KafkaConsumer(
    topic_name,
    bootstrap_servers=[config.kafka_ip],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    security_protocol="SSL",
    ssl_cafile="root.crt",      
    ssl_certfile=None,                 
    ssl_keyfile=None                   
)

for message in c:
    print("Message:", message.value.decode("utf-8"))

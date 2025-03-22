import json
import config
from kafka import KafkaProducer

topic_name = "TEST"

p = KafkaProducer(
    bootstrap_servers = [config.kafka_ip]
)

json_mess = json.dumps({"Name":"Alice"})

p.send( topic_name, json_mess.encode("utf-8"))
p.flush()

print("Sent")

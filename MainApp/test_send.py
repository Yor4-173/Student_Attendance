import json
import config
from kafka import KafkaProducer

topic_name = "TEST"

p = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    security_protocol="SSL",
    ssl_cafile="root.crt",                 # Truststore (CA cert)
    ssl_certfile=None,                             # Nếu client có cert riêng thì điền vào
    ssl_keyfile=None                               # Nếu client có key riêng thì điền vào
)

json_mess = json.dumps({"Name": "Alice"})

p.send(topic_name, json_mess.encode("utf-8"))
p.flush()

print("Sent")

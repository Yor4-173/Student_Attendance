sudo docker exec -it kafka bash
kafka-topics --create --bootstrap-server 192.168.43.58:9093 replication-factor 1 --partitions 1 --topic TEST  --command-config /etc/kafka/secrets/run.properties
kafka-console-producer   --broker-list 192.168.43.58:9093   --topic TEST   --producer.config /etc/kafka/secrets/run.properties
kafka-console-consumer   --bootstrap-server 192.168.43.58:9093   --topic TEST --from-beginning --partition 0   --consumer.config /etc/kafka/secrets/run.properties

kafka-topics --create --bootstrap-server 192.168.43.58:9093 replication-factor 1 --partitions 1 --topic SEND  --command-config /etc/kafka/secrets/run.properties
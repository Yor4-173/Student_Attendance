1. kafka-topics --create --bootstrap-server localhost:9093 replication-factor 1 --partitions 1 --topic TEST  --command-config /etc/kafka/secrets/run.properties
2. kafka-console-producer   --broker-list localhost:9093   --topic TEST   --producer.config /etc/kafka/secrets/run.properties
3. kafka-console-consumer   --bootstrap-server localhost:9093   --topic TEST --from-beginning --partition 0   --consumer.config /etc/kafka/secrets/run.properties

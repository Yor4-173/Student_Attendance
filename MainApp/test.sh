#!/bin/bash
# This script is used to create Kafka topics for the RASP application.
sudo docker exec -it kafka bash
kafka-topics --list --bootstrap-server 192.168.43.58:9093
kafka-topics --create --bootstrap-server 192.168.43.58:9093 replication-factor 1 --partitions 1 --topic RASP_SEND  --command-config /etc/kafka/secrets/run.properties
kafka-topics --create --bootstrap-server 192.168.43.58:9093 replication-factor 1 --partitions 1 --topic RASP_RECEIVE  --command-config /etc/kafka/secrets/run.properties

#no ssl
kafka-topics --create --bootstrap-server 192.168.43.58:9092 --replication-factor 1 --partitions 1 --topic RASP_SEND
kafka-topics --create --bootstrap-server 192.168.43.58:9092 --replication-factor 1 --partitions 1 --topic RASP_RECEIVE


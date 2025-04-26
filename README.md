# Student_Attendance

This project implements a Kafka-based client that captures images from a camera, sends them to a Kafka topic, and processes received results in real-time using YOLO object detection models. Designed for Raspberry Pi and similar edge devices.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Installation
Clone the repository:

```bash
git clone https://github.com/Yor4-173/Student_Attendance.git
cd Student_Attendance
pip install -r requirements.txt
```

## Configuration

Update `config.py` with your Kafka server IP.
This project requires SSL certificates to establish a secure connection with the Kafka server.

To generate the necessary SSL certificates, first:
```bash
sudo nano install_ca.sh
```
Change this into your own IPv4 Address:
```bash
# Set IP address as variable
IP_ADDR="192.168.43.58"
PASSWORD="password"
```

Next run:

```bash
./install_ca.sh
mkdir certs
mv kafka* key* trutstore_creds run.properties certs/
```

In `docker-compose.yml` change the IP:
 ```bash
 KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.43.58:9092,SSL://192.168.43.58:9093
 ```

To create Kafka Broker on Docker, run:

```bash
sudo docker-compose up -d
```
Run command in `test.sh` to create topic, remember change IP to your Machine Ip.

## Usage

To run Egde server run:

```bash
python sv_debug.py
```
To run raspberry client:

```bash
python raspberry_client.py
```

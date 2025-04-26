from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from flask import Flask
from flask import render_template , request
from flask_cors import CORS, cross_origin
import tensorflow as tf
import argparse
import facenet
import os
import sys
import math
import pickle
import align.detect_face
import numpy as np
import cv2
from kafka import KafkaConsumer, KafkaProducer
import config
import collections
from sklearn.svm import SVC
import base64
import json
import paho.mqtt.client as mqtt
import time
from datetime import datetime

THINGSBOARD_TOKEN = 'BqlbHOO9sXWI0hmTotYY'                 #Token of your device
THINGSBOARD_HOST = "mqtt.thingsboard.cloud"   	            #host result
THINGSBOARD_PORT = 1883 					    #data listening port
MQTT_TOPIC = "v1/devices/me/telemetry"

MINSIZE = 20
THRESHOLD = [0.6, 0.7, 0.7]
FACTOR = 0.709
IMAGE_SIZE = 182
INPUT_IMAGE_SIZE = 160
CLASSIFIER_PATH = 'model/Models/facemodel.pkl'
FACENET_MODEL_PATH = './model/Models/20180402-114759.pb'

# Load The Custom Classifier
with open(CLASSIFIER_PATH, 'rb') as file:
    model, class_names = pickle.load(file)
print("Custom Classifier, Successfully loaded")

with tf.Graph().as_default():

    # Cai dat GPU neu co
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.6)
    sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

    with sess.as_default():
        # Load the model
        print('Loading feature extraction model')
        facenet.load_model(FACENET_MODEL_PATH)
        images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
        embedding_size = embeddings.get_shape()[1]
        pnet, rnet, onet = align.detect_face.create_mtcnn(sess, None)


topic_name_in = "receive_result"
c = KafkaConsumer(
    topic_name_in,
    bootstrap_servers = [config.kafka_ip],
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    fetch_max_bytes = 9000000,
    fetch_max_wait_ms = 10000,
)

topic_name_out = "send_result"
p = KafkaProducer(
    bootstrap_servers=[config.kafka_ip],
    max_request_size = 9000000,
)


# Define MQTT connection callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to Thingsboard MQTT broker successfully!")
    else:
        print(f"Failed to connect to Thingsboard MQTT broker. Error code: {rc}")

def on_disconnect(client, userdata, rc, properties=None):
    if rc != 0:
        print("Unexpected disconnection from Thingsboard MQTT broker.")


for message in c:
    stream = message.value
    data = json.loads(stream)
    f = data['image']
    room = data['RoomID']

    name="Unknown"
    
    decoded_string = base64.b64decode(f)
    frame = np.fromstring(decoded_string, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_ANYCOLOR)

    bounding_boxes, _ = align.detect_face.detect_face(frame, MINSIZE, pnet, rnet, onet, THRESHOLD, FACTOR)

    faces_found = bounding_boxes.shape[0]

    if faces_found > 0:
        det = bounding_boxes[:, 0:4]
        margin = 32
        bb = np.zeros((faces_found, 4), dtype=np.int32)
        for i in range(faces_found):
            bb[i][0] = det[i][0]
            bb[i][1] = det[i][1]
            bb[i][2] = det[i][2]
            bb[i][3] = det[i][3]
            cropped = frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :]
            scaled = cv2.resize(cropped, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),
                                interpolation=cv2.INTER_CUBIC)
            scaled = facenet.prewhiten(scaled)
            scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
            feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
            emb_array = sess.run(embeddings, feed_dict=feed_dict)
            predictions = model.predict_proba(emb_array)
            best_class_indices = np.argmax(predictions, axis=1)
            best_class_probabilities = predictions[
                np.arange(len(best_class_indices)), best_class_indices]
            best_name = class_names[best_class_indices[0]]
            print("Name: {}, Probability: {}".format(best_name, best_class_probabilities))

            if best_class_probabilities > 0.5:
                name = class_names[best_class_indices[0]]
            else:
                name = "Unknown"

        buffer = {
            "name": name,
            "room": room
        }
        
        p.send(topic_name_out, json.dumps(buffer).encode('utf-8'))
        print("Result sended!")
        p.flush()
# MQTT client setup
        client = mqtt.Client(protocol=mqtt.MQTTv5)
        client.username_pw_set(THINGSBOARD_TOKEN)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
# Connect to Thingsboard MQTT broker
        client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        client.publish("v1/devices/me/telemetry", json.dumps(buffer))
        print("Telemetry data published successfully!")




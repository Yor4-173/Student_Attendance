#!/bin/bash

# Set IP address as variable
IP_ADDR="192.168.43.58"
PASSWORD="password"

echo "Creating CA..."
openssl genrsa -out root.key 2048
openssl req -new -x509 -key root.key -out root.crt -days 3650 -subj "/C=VN/ST=HN/L=HN/O=IT/CN=ca"

echo "Creating server certs for IP $IP_ADDR..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=VN/ST=HN/L=HN/O=IT/CN=$IP_ADDR"
openssl x509 -req -in server.csr -CA root.crt -CAkey root.key -CAcreateserial \
  -out server.crt -days 3650 \
  -extfile <(printf "subjectAltName=IP:$IP_ADDR")

echo "Creating client certs..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/C=VN/ST=HN/L=HN/O=IT/CN=client"
openssl x509 -req -in client.csr -CA root.crt -CAkey root.key -CAcreateserial \
  -out client.crt -days 3650 \
  -extfile <(printf "subjectAltName=DNS:localhost")

echo "Creating server keystore..."
keytool -keystore kafka.keystore.jks -alias kafka -validity 3650 -genkey -keyalg RSA \
  -dname "CN=$IP_ADDR, OU=IT, O=IT, L=HN, ST=HN, C=VN" \
  -storepass $PASSWORD -keypass $PASSWORD

keytool -keystore kafka.keystore.jks -alias kafka -certreq -file kafka.csr -storepass $PASSWORD
openssl x509 -req -in kafka.csr -CA root.crt -CAkey root.key -CAcreateserial \
  -out kafka-signed.crt -days 3650 \
  -extfile <(printf "subjectAltName=IP:$IP_ADDR")

keytool -keystore kafka.keystore.jks -alias CARoot -import -file root.crt -storepass $PASSWORD -noprompt
keytool -keystore kafka.keystore.jks -alias kafka -import -file kafka-signed.crt -storepass $PASSWORD -keypass $PASSWORD -noprompt

echo "Creating client keystore..."
keytool -keystore client.keystore.jks -alias client -validity 3650 -genkey -keyalg RSA \
  -dname "CN=client, OU=IT, O=IT, L=HN, ST=HN, C=VN" -storepass $PASSWORD -keypass $PASSWORD

keytool -keystore client.keystore.jks -alias client -certreq -file client-csr.jks -storepass $PASSWORD
openssl x509 -req -in client-csr.jks -CA root.crt -CAkey root.key -CAcreateserial \
  -out client-signed.crt -days 3650 \
  -extfile <(printf "subjectAltName=DNS:localhost")

keytool -keystore client.keystore.jks -alias CARoot -import -file root.crt -storepass $PASSWORD -noprompt
keytool -keystore client.keystore.jks -alias client -import -file client-signed.crt -storepass $PASSWORD -keypass $PASSWORD -noprompt

echo "Creating truststore..."
keytool -keystore kafka.truststore.jks -alias CARoot -import -file root.crt -storepass $PASSWORD -noprompt

echo "Writing credentials to files..."
echo $PASSWORD > keystore_creds
echo $PASSWORD > key_creds
echo $PASSWORD > truststore_creds

echo "✅ SSL setup completed for IP $IP_ADDR"

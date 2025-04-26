#!/bin/bash

echo "Creating CA..."
openssl genrsa -out root.key
openssl req -new -x509 -key root.key -out root.crt -days 3650 -subj "/C=VN/ST=HN/L=HN/O=IT/CN=ca"

echo "Creating server certs..."
openssl genrsa -out server.key
openssl req -new -key server.key -out server.csr -subj "/C=VN/ST=HN/L=HN/O=IT/CN=localhost"
openssl x509 -req -in server.csr -CA root.crt -CAkey root.key -CAcreateserial -out server.crt -days 3650 -extfile <(printf "subjectAltName=DNS:localhost")

echo "Creating client certs..."
openssl genrsa -out client.key
openssl req -new -key client.key -out client.csr -subj "/C=VN/ST=HN/L=HN/O=IT/CN=localhost"
openssl x509 -req -in client.csr -CA root.crt -CAkey root.key -CAcreateserial -out client.crt -days 3650 -extfile <(printf "subjectAltName=DNS:localhost")

echo "Creating server keystore..."
keytool -keystore kafka.keystore.jks -alias localhost -validity 3650 -genkey -keyalg RSA -dname "CN=localhost, OU=IT, O=IT, L=HN, ST=HN, C=VN" -storepass password -keypass password
keytool -keystore kafka.keystore.jks -alias localhost -certreq -file kafka.csr -storepass password -keypass password
openssl x509 -req -CA root.crt -CAkey root.key -in kafka.csr -out kafka-signed.crt -days 3650 -CAcreateserial
keytool -keystore kafka.keystore.jks -alias CARoot -import -file root.crt -storepass password -noprompt
keytool -keystore kafka.keystore.jks -alias localhost -import -file kafka-signed.crt -storepass password -keypass password -noprompt

echo "Creating client keystore..."
keytool -keystore client.keystore.jks -alias localhost -validity 3650 -genkey -keyalg RSA -dname "CN=localhost, OU=IT, O=IT, L=HN, ST=HN, C=VN" -storepass password -keypass password
keytool -keystore client.keystore.jks -alias localhost -certreq -file client.csr -storepass password -keypass password
openssl x509 -req -CA root.crt -CAkey root.key -in client.csr -out client-signed.crt -days 3650 -CAcreateserial
keytool -keystore client.keystore.jks -alias CARoot -import -file root.crt -storepass password -noprompt
keytool -keystore client.keystore.jks -alias localhost -import -file client-signed.crt -storepass password -keypass password -noprompt

echo "Creating truststore..."
keytool -keystore kafka.truststore.jks -alias CARoot -import -file root.crt -storepass password -noprompt

echo "Writing credentials to files..."
echo password > keystore_creds
echo password > key_creds
echo password > truststore_creds

echo "SSL setup completed."


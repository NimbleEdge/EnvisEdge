#!/bin/bash

read -p "Enter path to kafka Directory : " DIR 
read -p "kafka url: " URL

cd ${DIR}/
echo "Creating Topics..."
bin/kafka-topics.sh --create --topic job-request-aggregator --bootstrap-server ${URL}:9092 --partitions 4 --replication-factor 1
bin/kafka-topics.sh --create --topic job-request-trainer --bootstrap-server ${URL}:9092 --partitions 4 --replication-factor 1
bin/kafka-topics.sh --create --topic job-response-aggregator --bootstrap-server ${URL}:9092 --partitions 4 --replication-factor 1
bin/kafka-topics.sh --create --topic job-response-trainer --bootstrap-server ${URL}:9092 --partitions 4 --replication-factor 1

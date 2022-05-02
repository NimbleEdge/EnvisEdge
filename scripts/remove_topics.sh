#!/bin/bash

read -p "Enter path to kafka Directory : " DIR 
read -p "kafka url : " URL

cd ${DIR}/
echo "Removing Topics..."
bin/kafka-topics.sh --delete --topic job-response-trainer --bootstrap-server ${URL}:9092
bin/kafka-topics.sh --delete --topic job-request-trainer --bootstrap-server ${URL}:9092
bin/kafka-topics.sh --delete --topic job-request-aggregator --bootstrap-server ${URL}:9092
bin/kafka-topics.sh --delete --topic job-response-aggregator --bootstrap-server ${URL}:9092

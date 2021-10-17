from time import sleep
from json import dumps
from kafka import KafkaProducer


class Producer():

	def __init__(self):
		self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
    					value_serializer=lambda x: dumps(x).encode('utf-8'))



	def send_message(self, message):
		self.producer.send('1_topic_test', value=message)
		

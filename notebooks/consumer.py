from kafka import KafkaConsumer
from json import loads
from time import sleep





class Consumer():

	def __init__(self):
		self.consumer = KafkaConsumer('1_topic_test', bootstrap_servers=['localhost:9092'],
					    auto_offset_reset='earliest',
					    enable_auto_commit=True,
					    group_id='my-group-id',
					    value_deserializer=lambda x: loads(x.decode('utf-8')))


	def receive_message(self):
		for event in self.consumer:
		    event_data = event.value
		return event_data  


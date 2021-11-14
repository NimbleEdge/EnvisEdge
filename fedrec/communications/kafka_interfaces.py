from fedrec.communications.abstract_comm_manager import \
    AbstractCommunicationManager
from fedrec.utilities import registry
from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps

@registry.load("communications", "kafka")
class Kafka(AbstractCommunicationManager):
    def __init__(self,
                 consumer=True,
                 producer=True,
                 consumer_port=9092,
                 consumer_url="127.0.0.1",
                 consumer_topic=None,
                 consumer_group_id=None,
                 producer_port=9092,
                 producer_url="127.0.0.1",
                 producer_topic=None):
        if producer:
            self.producer_url = "{}:{}".format(
                producer_url, producer_port)
            self.producer = KafkaProducer(
                bootstrap_servers=[self.producer_url],
                value_serializer=lambda x: dumps(x).encode('utf-8'))
            self.producer_topic = producer_topic

        if consumer:
            self.consumer_url = "{}:{}".format(
                consumer_url, consumer_port)
            self.consumer = KafkaConsumer(
                consumer_topic,
                bootstrap_servers=[self.consumer_url],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=consumer_group_id,
                value_deserializer=lambda x: loads(x.decode('utf-8')))

    def receive_message(self):
        if not self.consumer:
            raise Exception("No consumer defined")
        return next(self.consumer)

    def send_message(self, message):
        if not self.producer:
            raise Exception("No producer defined")
        self.producer.send(self.producer_topic, value=message)

    def finish(self):
        self.producer.close()
        self.consumer.close()
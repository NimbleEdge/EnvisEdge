from fedrec.communications.abstract_comm_manager import \
    AbstractCommunicationManager
from fedrec.utilities import registry
from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps


@registry.load("communications", "kafka")
class Kafka(AbstractCommunicationManager):
    """
    Kafka specific methods below here.  These are not part of the abstract class.

    Attributes:
    ----------
    serializer: AbstractSerializer
        The serializer to use.
    consumer: KafkaConsumer
        The consumer to use.
    producer: KafkaProducer
        The producer to use.
    consumer_url: str
        The url of the consumer.
    consumer_port: int  
        The port of the consumer.
    consumer_topic: str
        The topic of the consumer.
    producer_url: str
        The url of the producer.
    producer_port: int
        The port of the producer.
    producer_topic: str 
        The topic of the producer.

    Methods:
    --------
    receive_message():
        Receives a message from the consumer.
    send_message(message):
        Sends a message to the producer.
    finish():
        Closes the consumer and producer.
    """
    def __init__(self,
                 serializer="json",
                 consumer=True,
                 producer=True,
                 consumer_port=9092,
                 consumer_url="127.0.0.1",
                 consumer_topic=None,
                 consumer_group_id=None,
                 producer_port=9092,
                 producer_url="127.0.0.1",
                 producer_topic=None):
        self.serializer = registry.construct("serializer", serializer)
        if producer:
            self.producer_url = "{}:{}".format(
                producer_url, producer_port)
            self.producer = KafkaProducer(
                bootstrap_servers=[self.producer_url],
                value_serializer=self.serializer.serialize)
            self.producer_topic = producer_topic

        if consumer:
            self.consumer_url = "{}:{}".format(
                consumer_url, consumer_port)
            self.consumer = KafkaConsumer(
                consumer_topic,
                bootstrap_servers=[self.consumer_url],
                value_deserializer=self.serializer.deserialize,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=consumer_group_id)

    def receive_message(self):
        """
        Receives a message from the consumer.
        
        Returns:
        --------
        message: object
            The message received.
        """
        if not self.consumer:
            raise Exception("No consumer defined")
        return next(self.consumer).value

    def send_message(self, message):
        """
        Sends a message to the producer.

        Returns:
        --------
        message: object
            The message sent.
        """
        if not self.producer:
            raise Exception("No producer defined")
        self.producer.send(self.producer_topic, value=message)

    def finish(self):
        """
        Closes the consumer and producer.
        """
        self.producer.close()
        self.consumer.close()
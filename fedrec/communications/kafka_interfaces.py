from fedrec.communications.abstract_comm_manager import \
    AbstractCommunicationManager
from fedrec.utilities import registry
from kafka import KafkaConsumer, KafkaProducer
from json import loads, dumps


@registry.load("communications", "kafka")
class Kafka(AbstractCommunicationManager):
    """
    Kafka specific methods below here. These are not part of the
    abstract class.

    Attributes:
    ----------
    serializer: AbstractSerializer
        The serializer to use.
    consumer: KafkaConsumer
       Consumer will get the message token form kafka broker.
    producer: KafkaProducer
        Producer will provide the message token to the kafka
        broker.
    consumer_url: str
        URL to which consumer will connects to get the message token.
    consumer_port: int
        Port where the consumer connect to get token.
    consumer_topic: str
        Topic to which consumer will subscribe to get the message
        token.
    consumer_group_id: str
        Group is used to identify the consumer group.
    producer_url: str
        URL to which consumer will connect to send the message token.
    producer_port: int
        Port where the producer connects to send the message
        token.
    producer_topic: str
        Topic to which producer will subscribe to send message token
        to consumer subscribed to that topic.

    Raises:
    -------
    Exception
        If the consumer or producer is set to `False`.
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
"""ZeroMQ messaging library used in distributed or 
concurrent applications and provides a message queue, 
capable of running without a dedicated message broker.
"""
import zmq
from zmq import Context
from fedrec.utilities import registry
from fedrec.communication_interfaces.abstract_comm_manager import \
    AbstractCommunicationManager

@registry.load("communication_interface", "ZeroMQ")
class ZeroMQ(AbstractCommunicationManager):
    def __init__(self,
                 subscriber=True,
                 publisher=True,
                 subscriber_port=2000,
                 subscriber_url="127.0.0.1",
                 subscriber_topic=None,
                 publisher_port=2000,
                 publisher_url="127.0.0.1",
                 publisher_topic=None,
                 protocol="tcp"):
        """
        Setting up a ZeroMQ publisher and subscriber using 
        the connection details.
        Parameters
        ----------
        subscriber : object
            specifies it needs a ZeroMQ subscriber
        publisher : object
            specifies it needs a ZeroMQ publisher
        """
        self.context = Context()

        if subscriber:
            self.subscriber_url = "{}://{}:{}".format(
                protocol, subscriber_url, subscriber_port)
            self.subscriber = self.context.socket(zmq.SUB)
            self.subscriber.setsockopt(zmq.SUBSCRIBE, subscriber_topic)
            self.subscriber.connect(self.subscriber_url)

        if publisher:
            self.publisher_url = "{}://{}:{}".format(
                protocol, publisher_url, publisher_port)
            self.publisher = self.context.socket(zmq.PUB)
            self.publisher.connect(self.publisher_url)

    def receive_message(self):
        """
        Receives a message from the ZeroMQ subscriber
        """
        if not self.subscriber:
            raise Exception("No subscriber defined")
        return self.subscriber.recv_multipart()

    def send_message(self, message):
        """
        Sends a message to the ZeroMQ publisher after 
        receiving from the subscriber.
        Parameters
        ----------
        message : object
            Publishes a message to the zeromq publisher
        """
        if not self.publisher:
            raise Exception("No publisher defined")
        self.publisher.send_pyobj(message)

    def close(self):
        """
        This function is called at the end to close the 
        connection and terminate the context.
        """
        if self.publisher:
            self.publisher.close()
        elif self.subscriber:
            self.subscriber.close()
        self.context.term()

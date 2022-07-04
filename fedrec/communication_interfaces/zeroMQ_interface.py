import zmq
from zmq import Context
from fedrec.utilities import registry
from fedrec.communication_interfaces.abstract_comm_manager import \
    AbstractCommunicationManager

@registry.load("communication_interface", "ZeroMQ")
class ZeroMQ(AbstractCommunicationManager):
    """
    ZeroMQ class implements the basic send/receive interface
    between the publisher and the subscriber. Senders of
    messages token are called publishers and the one who
    receives these tokens are called subscribers.

    Example
    -------
    >>> import zmq

    >>> context = zmq.Context()
    >>> print("Connecting to envisedge server…")
    >>> socket = context.socket(zmq.REQ)
    >>> socket.connect("tcp://localhost:5555")

    >>> for request in range(10):
    >>>     print("Sending request %s …" % request)
    >>>     socket.send(b"Hello")

    >>>     message = socket.recv()
    >>>     print("Received reply %s [ %s ]" % (request, message))

    Example
    -------
    >>> import time
    >>> import zmq

    >>> context = zmq.Context()
    >>> socket = context.socket(zmq.REP)
    >>> socket.bind("tcp://*:5555")

    >>> while True:
    >>>      message = socket.recv()
    >>>      print("Received request: %s" % message)
    >>>      time.sleep(1)
    >>>      socket.send(b"World")

    Parameters
    ----------
    subscriber: ZeroMQSubscriber
        Subscriber will get the message token from ZeroMQ broker
    publisher: ZeroMQProducer
        Publisher will send the message token to ZeroMQ broker
    subscriber_port: int
        Port where the subscriber connects to get token
    subscriber_url: str
        URL to which subscriber will connect to get the message token.
    subscriber_topic: str
        Topic to which subscriber will subscribe to fetches its message.
    publisher_port: int
        Port where the publisher connects to send message
    publisher_url: str
        URL to which publisher will connect to send the message token.
    publisher_topic: str
        Topic to which publisher will subscribe to send message token.
    protocol:str

    """
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
        Receives a message from the ZeroMQ broker.

        Returns
        --------
        message: object
            The message received.

        """

        if not self.subscriber:
            raise Exception("No subscriber defined")
        return self.subscriber.recv_multipart()

    def send_message(self, message):
        """
        Sends a message to the ZeroMQ broker.

        Returns
        -------
        message: object
            The message sent.

        """

        if not self.publisher:
            raise Exception("No publisher defined")
        self.publisher.send_pyobj(message)

    def close(self):
        if self.publisher:
            self.publisher.close()
        elif self.subscriber:
            self.subscriber.close()
        self.context.term()

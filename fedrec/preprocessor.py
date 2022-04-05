from abc import ABC, abstractmethod

import torch

from fedrec.utilities import registry


class PreProcessor(ABC):
     """
        defining our abstract base class ‘Preproceessor' which takes ABC as an argument
     """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def preprocess_data(self):
        pass

    @abstractmethod
    def load(self):
        pass

    def load_data_description(self):
        pass

    @abstractmethod
    def datasets(self, *splits):
        pass


@registry.load('preproc', 'dlrm')
class DLRMPreprocessor(PreProcessor):
     """
    The DLRM model handles continuous (dense) and categorical (sparse) features that describe users and products
    Attributes:
    ----------
    serializer: AbstractSerializer
        The serializer to use.
    consumer: KafkaConsumer
       Consumer will get the message token from kafka broker.
    producer: KafkaProducer
        Producer will provide the message token to the kafka
        broker.
    consumer_url: str
        URL to which consumer will connect to get the message token.
    consumer_port: int
        Port where the consumer connects to get token.
    consumer_topic: str
        Topic to which consumer will subscribe to fetches its message.
    consumer_group_id: str
        Group is used to identify the consumer group.
    producer_url: str
        URL to which producer will connect to send the message token.
    producer_port: int
        Port where the producer connects to send the message
        token.
    producer_topic: str
        Topic to which producer will subscribe to send message token.
    Raises:
    -------
    Exception
        If the consumer or producer is set to `False`.
    """  
     
    def __init__(
            self,
            datafile,
            output_file,
            dataset_config):
        self.dataset_config = dataset_config
        self.datafile = datafile
        self.output_file = output_file
        self.dataset_processor = registry.construct(
            'dset_proc', self.dataset_config,
            unused_keys=(),
            datafile=self.datafile,
            output_file=self.output_file)
        self.m_den = None
        self.n_emb = None
        self.ln_emb = None

    def preprocess_data(self):
        self.dataset_processor.process_data()
        if not self.m_den:
            self.load_data_description()

    def load_data_description(self):
        self.dataset_processor.load_data_description()
        self.m_den = self.dataset_processor.m_den
        self.n_emb = self.dataset_processor.n_emb
        self.ln_emb = self.dataset_processor.ln_emb

    def load(self):
        self.dataset_processor.load()

    def datasets(self, *splits):
        assert all([isinstance(split, str) for split in splits])
        return {
            split: self.dataset_processor.dataset(split)
            for split in splits
        }

    def dataset(self, split):
        assert isinstance(split, str)
        return self.dataset_processor.dataset(split)

    def data_loader(self, data, **kwargs):
        return torch.utils.data.DataLoader(
            data, collate_fn=self.dataset_processor.collate_fn, **kwargs
        )

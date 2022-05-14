import torch
from fedrec.serialization.serializable_interface import Serializable
from fedrec.utilities import registry
from fedrec.utilities.registry import Registrable


@Registrable.register_class_ref
class EnvisPreProcessor(Serializable):
    """
    Class for preprocessing Envis

    Argument:
        Serializable-load PyTorch tensors and module states in Python
        and how to serialize Python modules so they can be loaded in C++.
    """
    def __init__(
            self,
            dataset_config,
            client_id=None) -> None:
        """
        Initialize the EnvisPreProcessor class.

        Argument
        -----------------

        dataset_config-It configures the dataset
        client_id-(int) It's just an id
        """
        super().__init__()
        self.client_id = client_id
        self.dataset_config = dataset_config

        self.dataset_processor = registry.construct(
            'dataset', self.dataset_config,
            unused_keys=())

    def preprocess_data(self):
        """ It's used for preprocessing the data"""
        self.dataset_processor.process_data()

    def load(self):
        """It's used for loading the data"""
        self.dataset_processor.load(self.client_id)

    def load_data_description(self):
        """It's used for loading description of the data"""
        pass

    def datasets(self, *splits):
        """It splits the dataset
        Returns
        -----------
        split:The value by which the dataset should be splitted
        """
        assert all([isinstance(split, str) for split in splits])
        return {
            split: self.dataset_processor.dataset(split)
            for split in splits
        }

    def dataset(self, split):
        """It's used to get the splitted dataset.
        Arguments
        ------------

        split-(int):It's the value by which the dataset should be splitted.
        Returns
        ------------
        dataset_processor.dataset(split)-The splitted dataset.
        """
        assert isinstance(split, str)
        return self.dataset_processor.dataset(split)

    def data_loader(self, data, **kwargs):
        """
        It loads the data.
        Argument
        ------------
        data:The input data.
        **kwargs: Arbitrary keyword arguments.


        Returns:
        torch.utils.data.DataLoader-Its a python iterable
        over a dataset supporting single- and multi-process Data Loading.
        """
        return torch.utils.data.DataLoader(
            data, **kwargs
        )

    def serialize(self):
        """It's used to serialize the dataset and
        append the proc_name ,clien_id and the dataset config.

        Returns
        --------
        output:Outputs the appended dataset.
        """
        output = self.append_type({
            "proc_name": self.type_name(),
            "client_id": self.client_id,
            "dataset_config": self.dataset_config
        })
        return output

    @classmethod
    def deserialize(cls, obj):
        """It's used to deserialize the dataset.
           Class method is used as its specific to
           particular instance but still
           involve the class in some way.
           it means to (unpickle) files.
           for configuring  file,we need
           object serialization and deserialization.

        Arguments
        ----------

        obj:An object

        Returns
        ----------
        preproc_cls:It returns the dataset config and client_id of the object
        """
        preproc_cls = Registrable.lookup_class_ref(obj['proc_name'])
        return preproc_cls(
            dataset_config=obj["dataset_config"],
            client_id=obj["client_id"])

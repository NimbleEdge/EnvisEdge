import torch
from fedrec.user_modules.envis_preprocessor import EnvisPreProcessor
from fedrec.utilities import registry


@registry.load('preproc', 'dlrm')
class DLRMPreprocessor(EnvisPreProcessor):
    REGISTERED_NAME = 'dlrm'

    def __init__(
            self,
            dataset_config,
            client_id=0):
        super().__init__(dataset_config, client_id)
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

    def data_loader(self, data, **kwargs):
        return torch.utils.data.DataLoader(
            data, collate_fn=self.dataset_processor.collate_fn, **kwargs
        )

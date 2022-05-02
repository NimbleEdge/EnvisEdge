from fedrec.user_modules.envis_preprocessor import EnvisPreProcessor
from fedrec.utilities import registry


@registry.load('preproc', 'regression')
class RegressionPreprocessor(EnvisPreProcessor):

    def __init__(
            self,
            dataset_config,
            client_id=0):
        super().__init__(dataset_config, client_id)

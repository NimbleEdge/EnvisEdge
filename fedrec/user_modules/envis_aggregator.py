from fedrec.user_modules.envis_base_module import EnvisBase


class EnvisAggregator(EnvisBase):
    """
    Class for aggregating Envis.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError('__call__ method not implemented.')

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

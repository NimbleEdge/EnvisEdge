from fedrec.user_modules.envis_base_module import EnvisBase
""" EnvisAggregator class
Aggregates data from multiple Envis modules
and provides a single output
"""


class EnvisAggregator(EnvisBase):
    """
    Class for aggregating Envis.
    """

    def __init__(self, **kwargs):
        """ Initialize the EnvisAggregator class.
        """
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        """ Call the EnvisAggregator class."""
        raise NotImplementedError('__call__ method not implemented.')

    def __repr__(self):
        """ Return a string representation of the EnvisAggregator class.
        """
        return '{}()'.format(self.__class__.__name__)

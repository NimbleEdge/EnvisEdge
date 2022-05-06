from fedrec.user_modules.envis_base_module import EnvisBase
""" EnvisAggregator class
Aggregates data from multiple Envis modules
and provides a single output
"""


class EnvisAggregator(EnvisBase):
    """
    Class for aggregating Envis.

    Args:
        module_list: List of Envis modules to aggregate.
    """

    def __init__(self, **kwargs):
        """ Initialize the EnvisAggregator class.

        Args:
            module_list: List of Envis modules to aggregate.
        """
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        """ Call the EnvisAggregator class.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        raise NotImplementedError('__call__ method not implemented.')

    def __repr__(self):
        """ Return a string representation of the EnvisAggregator class.

        Args:
            None.

        Returns:
            String representation of the EnvisAggregator class.
        """
        return '{}()'.format(self.__class__.__name__)

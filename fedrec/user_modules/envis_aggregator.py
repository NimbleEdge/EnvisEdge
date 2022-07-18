from fedrec.user_modules.envis_base_module import EnvisBase


class EnvisAggregator(EnvisBase):
    """
    This class is used to aggregate the results of multiple EnvisBase modules.
    By aggregating, we mean that we can combine the results of multiple modules
    into a single result. For example, we can aggregate the results of multiple
    modules that are trained on the same data set. We can also aggregate the
    results of multiple modules that are trained on different data sets.

    Methods
    -------
    __call__():
        Aggregate the results of the modules.
    __repr__():
        Return a string representation of the object.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError('__call__ method not implemented.')

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

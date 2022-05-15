# Mixed-Dimensions Trick
#
# Description: Applies mixed dimension trick to embeddings to reduce
# embedding sizes.
#
# References:
# [1] Antonio Ginart, Maxim Naumov, Dheevatsa Mudigere, Jiyan Yang, James Zou,
# "Mixed Dimension Embeddings with Application to Memory-Efficient
# Recommendation Systems", CoRR, arXiv:1909.11810, 2019
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from fedrec.utilities import registry
from torch.nn.parameter import Parameter


def md_solver(n, alpha, d0=None, B=None, round_dim=True, k=None):
    '''
    An external facing function call for mixed-dimension assignment
    with the alpha power temperature heuristic.

    Arguments
    ----------
    n(torch.LongTensor); Vector of num of rows for each embedding matrix
    alpha -- (torch.FloatTensor); Scalar, non-negative, controls dim. skew
    d0 -- (torch.FloatTensor); Scalar, baseline embedding dimension
    B -- (torch.FloatTensor); Scalar, parameter budget for embedding layer
    round_dim -- (bool); flag for rounding dims to nearest pow of 2
    k -- (torch.LongTensor) ; Vector of average number of queries per inference

    Return
    -------------
    d(int)-Returns the undo_sort of the alpha power rule
    '''
    n, indices = torch.sort(n)
    k = k[indices] if k is not None else torch.ones(len(n))
    d = alpha_power_rule(n.type(torch.float) / k, alpha, d0=d0, B=B)
    if round_dim:
        d = pow_2_round(d)
    undo_sort = [0] * len(indices)
    for i, v in enumerate(indices):
        undo_sort[v] = i
    return d[undo_sort]


def alpha_power_rule(n, alpha, d0=None, B=None):
    '''
    Rounds the baseline embedding dimension to its nearest integer

   Arguments
    ---------------
    n(torch.LongTensor) - ; Vector of num of rows for each embedding matrix
    alpha -- (torch.FloatTensor); Scalar, non-negative, controls dim. skew
    d0 -- (torch.FloatTensor); Scalar, baseline embedding dimension
    B -- (torch.FloatTensor); Scalar, parameter budget for embedding layer

    Returns
    --------
    torch.round(d).type(torch.long))(Tensor)-Rounds elements
    of input to the nearest integer.
    '''
    if d0 is not None:
        lamb = d0 * (n[0].type(torch.float) ** alpha)
    elif B is not None:
        lamb = B / torch.sum(n.type(torch.float) ** (1 - alpha))
    else:
        raise ValueError("Must specify either d0 or B")
    d = torch.ones(len(n)) * lamb * (n.type(torch.float) ** (-alpha))
    for i in range(len(d)):
        if i == 0 and d0 is not None:
            d[i] = d0
        else:
            d[i] = 1 if d[i] < 1 else d[i]
    return (torch.round(d).type(torch.long))


def pow_2_round(dims):
    '''
    Calculates to the power of 2

    Argument
    --------------
    dims -- (torch.LongTensor);takes dimension as input

    Return
    -------------
    2 ** torch.round(torch.log2(dims.type(torch.float))
    '''
    return 2 ** torch.round(torch.log2(dims.type(torch.float)))


@registry.load("embedding", "torch_bag")
class EmbeddingBag(nn.EmbeddingBag):
    """Computes sums or means over two bags of embeddings,
    one using the quotient of the indices and the other using the remainder
    of the indices, without instantiating the intermediate embeddings,
    then performsan operation to combine these.

    Attributes
    ----------
    nn.EmbeddingBag


    """
    def __init__(
            self,
            num_embeddings: int,
            embedding_dim: int,
            max_norm: Optional[float] = None,
            norm_type: float = 2.,
            scale_grad_by_freq: bool = False,
            mode: str = 'mean',
            sparse: bool = False,
            _weight: Optional[Tensor] = None,
            include_last_offset: bool = False,
            init=False) -> None:
        """
        Computes sums or means over two bags of embeddings,
        one using the quotient of the indices and the other using the
        remainder of the indices, without instantiating
        the intermediate embeddings, then performsan operation
        to combine these.

        Parameters
        -------------
        num_categories (int) -total number of unique categories.
        The input indices must be in 0, 1, …, num_categories - 1.
        embedding_dim (list)-list of sizes for each embedding
        vector in each table.If "add" or "mult" operation are used,
        these embedding dimensions must be the sameIf a single
        embedding_dim is used,then it will use this embedding_dim
        for both embedding tables.
        num_collisions (int)-number of collisions to enforce.
        operation (string, optional)-"concat", "add", or "mult".
        Specifies the operation to compose embeddings.
        ``"concat" concatenates the embeddings, "add" sums the embeddings
        and "mult" multiplies (component-wise) the embeddings.
        Default: "mult"
        max_norm (float, optional) -If given, each embedding vector with norm
        larger than max_norm is renormalized to have norm max_norm.
        norm_type (float, optional)The p of the p-norm to compute
        for the max_norm option. Default 2.scale_grad_by_freq
        (boolean, optional) if given, this will scale gradients by the inverse
        of frequency of the words in the mini-batch. Default False.
        """

        super().__init__(num_embeddings,
                         embedding_dim,
                         max_norm=max_norm,
                         norm_type=norm_type,
                         scale_grad_by_freq=scale_grad_by_freq,
                         mode=mode,
                         sparse=sparse,
                         _weight=_weight,
                         include_last_offset=include_last_offset)
        if init:
            # initialize embeddings
            with torch.no_grad():
                W = np.random.uniform(
                    low=-np.sqrt(1 / num_embeddings),
                    high=np.sqrt(1 / num_embeddings),
                    size=(num_embeddings, embedding_dim)).astype(np.float32)
                self.weight = Parameter(torch.tensor(W, requires_grad=True))


@registry.load("embedding", "pr_emb")
class PrEmbeddingBag(nn.Module):
    '''
    It is like adding a extra rapper layer upon the embedding
    nn.Module:Base class for all neural network modules.
    '''
    def __init__(self,
                 num_embeddings,
                 embedding_dim,
                 base_dim=None,
                 index=-1,
                 init=False):
        '''Base class for all neural network modules.Used for the function definition

    Arguments
    -----------------
        num_embeddings:(int)  size of the dictionary of embedding.
        embedding_dim:(int) the size of each embedding vector.
        base_dim-The base dimension.
        index:(int) -the particular index.
        '''
        super(PrEmbeddingBag, self).__init__()
        if base_dim is None:
            assert index >= 0, "PR emb either specify"
            + " base dimension or extraction index"
            base_dim = max(embedding_dim)
            embedding_dim = embedding_dim[index]
        self.embs = nn.EmbeddingBag(
            num_embeddings, embedding_dim, mode="sum", sparse=True)
        torch.nn.init.xavier_uniform_(self.embs.weight)
        if embedding_dim < base_dim:
            self.proj = nn.Linear(embedding_dim, base_dim, bias=False)
            torch.nn.init.xavier_uniform_(self.proj.weight)
        elif embedding_dim == base_dim:
            self.proj = nn.Identity()
        else:
            raise ValueError(
                "Embedding dim " + str(embedding_dim) +
                " > base dim " + str(base_dim)
            )

        if init:
            with torch.no_grad():
                # use np initialization as below for consistency...
                W = np.random.uniform(
                    low=-np.sqrt(1 / num_embeddings),
                    high=np.sqrt(1 / num_embeddings),
                    size=(num_embeddings, embedding_dim)
                ).astype(np.float32)
                self.embs.weight = Parameter(
                    torch.tensor(W, requires_grad=True))

    def forward(self, input, offsets=None, per_sample_weights=None):
        """
        Forward pass of EmbeddingBag.

        Arguments
        --------
        input (Tensor)Tensor containing bags of indices into the
        embedding matrix.offsets (Tensor, optional) Only used when
        input is 1D. offsets determines the starting index
        position of each bag (sequence) in input.
        per_sample_weights (Tensor, optional)  a tensor
        of float / double weights, or None to indicate all weights
        should be taken to be 1. If specified, per_sample_weights
        must have exactly the same shape as input and is treated
        as having the same offsets,if those are not None.
        Only supported for mode='sum'.

        Returns
        --------------
        Tensor output shape of (B, embedding_dim).
        """
        return self.proj(self.embs(
            input,
            offsets=offsets,
            per_sample_weights=per_sample_weights))


@registry.load("embedding", "qr_emb")
class QREmbeddingBag(nn.Module):
    r"""Computes sums or means over two 'bags' of embeddings,
        one using the quotient of the indices and the other
        using the remainder of the indices, without
        instantiating the intermediate embeddings,
        then performsan operation to combine these.

        For bags of constant length and no :attr:`per_sample_weights`, this class

            * with ``mode="sum"`` is equivalent to :class:`~torch.nn.Embedding` followed by ``sum(dim=1)``,
            * with ``mode="mean"`` is equivalent to :class:`~torch.nn.Embedding` followed by ``torch.mean(dim=1)``,
            * with ``mode="max"`` is equivalent to :class:`~torch.nn.Embedding` followed by ``torch.max(dim=1)``.

        However, :class:`~torch.nn.EmbeddingBag` is much more time and memory
        efficient than using a chain of these operations.

        QREmbeddingBag also supports per-sample weights as an argument
        to the forward pass. This scales the output of the Embedding
        before performing a weighted reduction as specified by ``mode``.

        If :attr:`per_sample_weights`` is passed, the only supported ``mode`` is
        ``"sum"``, which computes a weighted sum according to :attr:
        `per_sample_weights`.

        Known Issues:
        Autograd breaks with multiple GPUs. It breaks only with
        multiple embeddings.
    Args:
        num_categories (int): total number of unique categories.
            The input indices must be in 0, 1, ..., num_categories - 1.
        embedding_dim (list): list of sizes for each embedding vector in each table.
            If ``"add"`` or ``"mult"`` operation are used, these embedding
            dimensions must be the same.
            If a single embedding_dim is used, then it will use this
            embedding_dim for both embedding tables.
        num_collisions (int): number of collisions to enforce.
        operation (string, optional):
            ``"concat"``, ``"add"``, or ``"mult". Specifies the operation
            to compose embeddings. ``"concat"`` concatenates the embeddings,
            ``"add"`` sums the embeddings, and ``"mult"`` multiplies
            (component-wise) the embeddings.
            Default: ``"mult"``
        max_norm (float, optional):
            If given, each embedding vector with norm larger than
            :attr:`max_norm` is renormalized to have norm
            :attr:`max_norm`.
        norm_type (float, optional):
            The p of the p-norm to compute for the :attr:`max_norm` option.
            Default ``2``.
        scale_grad_by_freq (boolean, optional):
            if given, this will scale gradients by the inverse
            of frequency of the words in the mini-batch.
            Default ``False``.
            .. note::
                This option is not supported when ``mode="max"``.
        mode (string, optional):
            ``"sum"``, ``"mean"`` or ``"max"``. Specifies the way to reduce the
            bag.
            * ``"sum"`` computes the weighted sum, taking `per_sample_weights` into consideration.
            * ``"mean"`` computes the average of the values in the bag,
            * ``"max"`` computes the max value over each bag.
            Default: ``"mean"``
        sparse (bool, optional):
            if ``True``, gradient w.r.t. :attr:`weight` matrix
            will be a sparse tensor.
            See Notes for more details regarding sparse gradients.
            .. note::
                This option is not supported when ``mode="max"``.
    Attributes:
        weight (Tensor):
            the learnable weights of each embedding table
            is the module of shape `(num_embeddings, embedding_dim)`
            initialized using a uniform distribution
            with sqrt(1 / num_categories).
    Inputs:
        :attr:`input` (LongTensor), :attr:`offsets` (LongTensor, optional), and
            :attr:`per_index_weights` (Tensor, optional)
            If :attr:`input` is 2D of shape `(B, N)`,
            it will be treated as ``B`` bags (sequences) each of
            fixed length ``N``, and this will return ``B`` values
            aggregated in a way depending on the :attr:`mode`.
            :attr:`offsets` is ignored and required to be ``None``
            in this case.
            If :attr:`input` is 1D of shape `(N)`,
            it will be treated as a concatenation of multiple bags (sequences).
            :attr:`offsets` is required to be a 1D tensor containing the
            starting index positions of each bag in :attr:`input`. Therefore,
            for :attr:`offsets` of shape `(B)`, :attr:`input` will be viewed as
            having ``B`` bags. Empty bags (i.e., having 0-length) will have
            returned vectors filled by zeros.
        per_sample_weights (Tensor, optional):
            a tensor of float / double weights, or None
            to indicate all weights should be taken to be ``1``.
            If specified, :attr:`per_sample_weights` must have exactly the
            same shape as input and is treated as having the same
            :attr:`offsets`, if those are not ``None``.
            Only supported for ``mode='sum'``.
    Returns:
        The output tensor of shape `(B, embedding_dim)`
    """  # noqa: E501

    __constants__ = ['num_embeddings',
                     'embedding_dim',
                     'num_collisions',
                     'operation',
                     'max_norm',
                     'norm_type',
                     'scale_grad_by_freq',
                     'mode', 'sparse']
    def __init__(self, num_embeddings,embedding_dim,
                num_collisions,operation='mult', max_norm=None,
                norm_type=2,scale_grad_by_freq=False,
                mode='mean', sparse=False,_weight=None):
        """__init__ function is called every time an object is created."""
    def __init__(self, num_embeddings, embedding_dim, num_collisions,
                 operation='mult', max_norm=None, norm_type=2.,
                 scale_grad_by_freq=False, mode='mean', sparse=False,
                 _weight=None):
        super(QREmbeddingBag, self).__init__()

        assert operation in ['concat', 'mult', 'add'], 'Not valid operation!'

        self.num_categories = num_embeddings
        if isinstance(embedding_dim, int) or len(embedding_dim) == 1:
            self.embedding_dim = [embedding_dim, embedding_dim]
        else:
            self.embedding_dim = embedding_dim
        self.num_collisions = num_collisions
        self.operation = operation
        self.max_norm = max_norm
        self.norm_type = norm_type
        self.scale_grad_by_freq = scale_grad_by_freq

        if self.operation == 'add' or self.operation == 'mult':
            assert self.embedding_dim[0] == self.embedding_dim[1], \
                'Embedding dimensions do not match!'

        self.num_embeddings = [int(np.ceil(num_embeddings / num_collisions)),
                               num_collisions]

        if _weight is None:
            self.weight_q = Parameter(torch.Tensor(
                self.num_embeddings[0], self.embedding_dim[0]))
            self.weight_r = Parameter(torch.Tensor(
                self.num_embeddings[1], self.embedding_dim[1]))
            self.reset_parameters()
        else:
            assert list(_weight[0].shape) == [self.num_embeddings[0],
                                              self.embedding_dim[0]], \
                'Shape of weight for quotient table does not'\
                + 'match num_embeddings and embedding_dim'
            assert list(_weight[1].shape) == [self.num_embeddings[1],
                                              self.embedding_dim[1]], \
                'Shape of weight for remainder table does not'\
                + 'match num_embeddings and embedding_dim'
            self.weight_q = Parameter(_weight[0])
            self.weight_r = Parameter(_weight[1])
        self.mode = mode
        self.sparse = sparse

    def reset_parameters(self):
        """ Its used for resetting the parameters."""
        nn.init.uniform_(self.weight_q,
                         np.sqrt(1 / self.num_categories))
        nn.init.uniform_(self.weight_r, np.sqrt(1 / self.num_categories))

    def forward(self, input, offsets=None, per_sample_weights=None):
        '''
        Defines the computation performed at every call.
        Should be overridden by all subclasses.

        Arguments
        ------------------
        input:long-Takes the input
        offsets:offsets determines the starting index position of
        each bag (sequence) in input.
        per_sample_weights:a tensor of double weights, or None to
        indicate all weights should be taken to be 1.

        Returns
        ----------------
        (int)The output tensor of shape (B, embedding_dim)
        '''
        input_q = (input / self.num_collisions).long()
        input_r = torch.remainder(input, self.num_collisions).long()

        embed_q = F.embedding_bag(
            input_q, self.weight_q, offsets, self.max_norm,
            self.norm_type, self.scale_grad_by_freq, self.mode,
            self.sparse, per_sample_weights
        )
        embed_r = F.embedding_bag(
            input_r, self.weight_r, offsets, self.max_norm,
            self.norm_type, self.scale_grad_by_freq, self.mode,
            self.sparse, per_sample_weights
        )

        if self.operation == 'concat':
            embed = torch.cat((embed_q, embed_r), dim=1)
        elif self.operation == 'add':
            embed = embed_q + embed_r
        elif self.operation == 'mult':
            embed = embed_q * embed_r

        return embed

    def extra_repr(self):
        """Set the extra representation of the module
            To print customized extra information, you should
            re-implement this method in your own modules.
            Both single-line and multi-line strings are acceptable.


            Returns
            ----------------------
            s.format()
            """
        def extra_repr(self):
            s = '{num_embeddings}, {embedding_dim}'
            if self.max_norm is not None:
                s += ', max_norm={max_norm}'
            if self.norm_type != 2:
                s += ', norm_type={norm_type}'
            if self.scale_grad_by_freq is not False:
                s += ', scale_grad_by_freq={scale_grad_by_freq}'
            s += ', mode={mode}'
            return s.format(**self.__dict__)

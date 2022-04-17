from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
# pytorch
import torch
from torch.utils.data import Dataset 
class CriteoDataset(Dataset):
    """Class docstrings go here"""





""""This class is used to represent the criteo dataset 


...
Attributes
-----------
X_int:
X_cat:its an array storing some tensor value
y:its an array storing some values
max_ind_range: for defining the maximum range of indices
    
Methods 
----------------------------------------------------------------
__getitem__
_default_preprocess
collate_wrapper_criteo_offset
offset_to_length_converter"""




    def __init__(                       
            self,                   
            X_int, X_cat, y,
            max_ind_range):               
        self.max_ind_range = max_ind_range
        self.X_int = X_int  #initializing or defining the variables
        self.X_cat = X_cat
        self.y = y

    def __getitem__(self, index): #_getitem_() allows its instances to use the [] (indexer) operators

        if isinstance(index, slice):
            return [
                self[idx] for idx in range(
                    index.start or 0, index.stop or len(self), index.step or 1
                )
            ]

        if self.max_ind_range > 0: #range should be greater than zero for returning the followinng paarmeters
            return (
                self.X_int[index],
                self.X_cat[index] % self.max_ind_range,
                self.y[index]
            )
        else:
            return self.X_int[index], self.X_cat[index], self.y[index]

    def _default_preprocess(self, X_int, X_cat, y):
        X_int = torch.log(torch.tensor(X_int, dtype=torch.float) + 1)
        if self.max_ind_range > 0:
            X_cat = torch.tensor(X_cat % self.max_ind_range, dtype=torch.long)
        else:
            X_cat = torch.tensor(X_cat, dtype=torch.long)
        y = torch.tensor(y.astype(np.float32))

        return X_int, X_cat, y #returns the integer variable and the categorical variable

    def __len__(self):
        return len(self.y) #returns the length


def collate_wrapper_criteo_offset(list_of_tuples):
    # where each tuple is (X_int, X_cat, y)
    transposed_data = list(zip(*list_of_tuples))#data represented in form of a list
    X_int = torch.log(torch.tensor(transposed_data[0], dtype=torch.float) + 1)#returns a new tensor with the natural logarithm of the elements of input
    X_cat = torch.tensor(transposed_data[1], dtype=torch.long)
    T = torch.tensor(transposed_data[2], dtype=torch.float32).view(-1, 1)

    batchSize = X_cat.shape[0]
    featureCnt = X_cat.shape[1]

    lS_i = [X_cat[:, i] for i in range(featureCnt)]#input
    lS_o = [torch.tensor(range(batchSize)) for _ in range(featureCnt)]#output

    return (X_int, torch.stack(lS_o), torch.stack(lS_i)), T

# Conversion from offset to length


def offset_to_length_converter(lS_o, lS_i):
    def diff(tensor):
        return tensor[1:] - tensor[:-1] #returns the length of the tensor

    return torch.stack(   #Concatenates a sequence of tensors along a new dimension.

        [
            diff(torch.cat((S_o, torch.tensor(lS_i[ind].shape))).int())#Concatenates the given sequence of seq tensors in the given dimension
            for ind, S_o in enumerate(lS_o)                             and computes the n-th forward difference along the given dimension#
        ]
    )


def collate_wrapper_criteo_length(list_of_tuples):
    # where each tuple is (X_int, X_cat, y)
    transposed_data = list(zip(*list_of_tuples))#Joins two tuples together
    X_int = torch.log(torch.tensor(transposed_data[0], dtype=torch.float) + 1)
    X_cat = torch.tensor(transposed_data[1], dtype=torch.long)#It creates a multi-dimensional matrix containing elements of a single data type.
    T = torch.tensor(transposed_data[2], dtype=torch.float32).view(-1, 1)#Returns a new tensor with the same data as the self tensor but of a different shape

    batchSize = X_cat.shape[0]
    featureCnt = X_cat.shape[1]

    lS_i = torch.stack([X_cat[:, i] for i in range(featureCnt)])#computes the categorical feature in the range of feature count
    lS_o = torch.stack(
        [torch.tensor(range(batchSize)) for _ in range(featureCnt)]
    )

    lS_l = offset_to_length_converter(lS_o, lS_i)
    return (X_int, lS_l, lS_i), T


def make_criteo_data_and_loaders(args, offset_to_length_converter=False):
    train_data = CriteoDataset(
        args.data_set,
        args.max_ind_range,
        args.data_sub_sample_rate,
        args.data_randomize,
        "train",
        args.raw_data_file,
        args.processed_data_file
    )

    test_data = CriteoDataset(           #defining the test data
        args.data_set,
        args.max_ind_range,
        args.data_sub_sample_rate,
        args.data_randomize,
        "test",
        args.raw_data_file,
        args.processed_data_file
    )

    collate_wrapper_criteo = collate_wrapper_criteo_offset
    if offset_to_length_converter:
        collate_wrapper_criteo = collate_wrapper_criteo_length

    train_loader = torch.utils.data.DataLoader(  #loading the  training parameter representing a Python iterable over a dataset, with support for
        train_data,
        batch_size=args.mini_batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=collate_wrapper_criteo,
        pin_memory=False,
        drop_last=False,  # True
    )

    test_loader = torch.utils.data.DataLoader(   #loading the testing parameters 
        test_data,
        batch_size=args.test_mini_batch_size,
        shuffle=False,
        num_workers=args.test_num_workers,
        collate_fn=collate_wrapper_criteo,
        pin_memory=False,
        drop_last=False,  # True
    )

    return train_data, train_loader, test_data, test_loader #returning the train data,train loader and test loader

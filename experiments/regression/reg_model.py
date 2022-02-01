import abc
import sys

import numpy as np
import torch
from fedrec.preprocessor import RegressionPreprocessor
from fedrec.utilities import registry
from torch import nn, sigmoid
from torch.nn.parameter import Parameter

### define LogisticRegression in PyTorch ###

@registry.load("model", "regression")
class Regression(nn.Module):
    Preproc = RegressionPreprocessor

    def __init__(
        self,
        preprocessor: RegressionPreprocessor,
        input_dim = 784, 
        output_dim = 10,
        loss_weights=None,
        loss_threshold=0.0,
        ndevices=-1,
        loss_function="mse"
    ):
        super(Regression, self).__init__()
        self.preproc = preprocessor
        self.ndevices = ndevices
        self.output_dim = output_dim
        self.input_dim = input_dim
        self.parallel_model_batch_size = -1
        self.parallel_model_is_not_prepared = True
        self.loss_threshold = loss_threshold
        self.loss_function = loss_function

        self.linear = torch.nn.Linear(self.input_dim,self.output_dim,True)
        

        # specify the loss function
        if self.loss_function == "mse":
            self.loss_fn = torch.nn.MSELoss(reduction="mean")
        elif self.loss_function == "bce":
            self.loss_fn = torch.nn.BCEWithLogitsLoss(
                reduction="mean", pos_weight=loss_weights)
        else:
            sys.exit(
                "ERROR: --loss_function="
                + self.loss_function
                + " is not supported"
            )
            

    def forward(self, x): #TODO: where are we calling this function?
        out = self.linear(x)

        if 0.0 < self.loss_threshold and self.loss_threshold < 1.0:
            out = torch.clamp(out, min=self.loss_threshold,
                              max=(1.0 - self.loss_threshold))
        return out

    def get_scores(self, logits):
        return sigmoid(logits)

    def loss(self, logits, true_label):
        if self.loss_function == "mse":
            return self.loss_fn(self.get_scores(logits), true_label)
        elif self.loss_function == "bce":
            return self.loss_fn(logits, true_label)

import logging
from typing import Dict

import numpy as np
from fedrec.python_executors.aggregator import Neighbour
from fedrec.user_modules.envis_base_module import EnvisBase
from fedrec.user_modules.envis_preprocessor import EnvisPreProcessor
from fedrec.utilities import registry
from fedrec.utilities.random_state import RandomContext


@registry.load('aggregator', 'fed_adam')
class FedAdam(EnvisBase):
    def __init__(self,
                 config_dict: Dict,
                 in_neighbours: Dict[int, Neighbour] = {},
                 out_neighbours: Dict[int, Neighbour] = {},
                 beta1: float = 0.9, beta2 : float = 0.99, lr : float = 0.01, eps = 0.001):
        super().__init__(config_dict)
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours
        self.config_dict = config_dict
        modelCls = registry.lookup('model', self.config_dict["model"])
        self.model_preproc: EnvisPreProcessor = registry.instantiate(
            modelCls.Preproc,
            self.config_dict["model"]['preproc'])

        with self.model_random:
            # 1. Construct model
            self.model_preproc.load_data_description()
            self.model = registry.construct(
                'model', self.config_dict["model"],
                preprocessor=self.model_preproc,
                unused_keys=('name', 'preproc')
            )
        self.momentum = {key:0 for key in ((self.in_neighbours)[0].model).keys()}
        self.v = {key:0 for key in ((self.in_neighbours)[0].model).keys()}
        self.beta1 = beta1
        self.beta2 = beta2
        self.lr = lr
        self.eps = eps

    def store_state(self):
        assert self.model is not None
        return {
            'model': self.model,
            'in_neighbours': self.in_neighbours,
        }

    def aggregate(self):
        model_list = [None] * len(self.in_neighbours.values())
        training_num = 0
        model_params = self.model.state_dict()
        for idx, neighbour in enumerate(self.in_neighbours.values()):
            model_list[idx] = (neighbour.sample_num, neighbour.model)
            training_num += neighbour.sample_num

        (sample_num0, averaged_params) = model_list[0]
        for k in averaged_params.keys():
            averaged_params[k] *= sample_num0/training_num
            for sample_num, params in model_list:
                averaged_params[k] += params[k] * (sample_num/training_num)
            delta = model_params[k] - averaged_params[k]
            self.momentum[k] = self.momentum[k]*self.beta1 + (1 - self.beta1)*delta
            self.v[k] = self.v[k]*self.beta2 + (1 - self.beta2)*(delta**2)
            model_params[k] = model_params[k] - self.lr*(self.momentum[k]/(self.v[k]**0.5) + eps)

        return model_params

    def sample_clients(self, round_idx, client_num_per_round):
        num_neighbours = len(self.in_neighbours)
        if num_neighbours == client_num_per_round:
            selected_neighbours = [
                neighbour for neighbour in self.in_neighbours]
        else:
            with RandomContext(round_idx):
                selected_neighbours = np.random.choice(
                    self.in_neighbours,
                    min(client_num_per_round, num_neighbours),
                    replace=False)
        logging.info("worker_indexes = %s" % str(selected_neighbours))
        return selected_neighbours

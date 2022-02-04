import logging
from typing import Dict

import numpy as np
from fedrec.python_executors.aggregator import Neighbour
from fedrec.utilities import registry
from fedrec.utilities.random_state import RandomContext


@registry.load('aggregator', 'fed_avg')
class FedAvg:
    def __init__(self,
                 in_neighbours: Dict[int, Neighbour] = None,
                 out_neighbours: Dict[int, Neighbour] = None):
        self.in_neighbours = in_neighbours
        self.out_neighbours = out_neighbours

    def test_run(self, arg1, arg2):
        return arg1 + arg2

    def aggregate(self):
        model_list = [None] * len(self.in_neighbours)
        training_num = 0
 
        for idx, neighbour in enumerate(self.in_neighbours.values()):
            model_list[idx] = neighbour.model
            training_num += neighbour.sample_num
 
        (sample_num0, averaged_params) = model_list[0]
        for k in averaged_params.keys():
            averaged_params[k] *= sample_num0/training_num
            for sample_num, params in model_list:
                averaged_params[k] += params[k] * (sample_num/training_num)
                
        return averaged_params

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

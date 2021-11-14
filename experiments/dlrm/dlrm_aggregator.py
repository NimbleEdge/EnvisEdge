from typing import Dict

import numpy as np
from fedrec.python_executors.aggregator import (Aggregator, AggregatorConfig,
                                                Neighbour)
from fedrec.utilities import registry
from fedrec.utilities.logger import BaseLogger
from fedrec.utilities.random_state import RandomContext


@registry.load('aggregator', 'fed_avg')
class FedAvg(Aggregator):
    def __init__(self,
                 worker_index: int,
                 model_config: Dict,
                 aggregator_config: AggregatorConfig,
                 logger: BaseLogger,
                 in_neighbours: Dict[int, Neighbour] = None,
                 out_neighbours: Dict[int, Neighbour] = None,
                 persistent_storage: str = None,
                 is_mobile: bool = True,
                 round_idx: int = 0):
        super().__init__(worker_index, model_config, aggregator_config, logger,
                         in_neighbours, out_neighbours, persistent_storage,
                         is_mobile, round_idx)

    def aggregate(self, neighbour_ids):
        model_list = [
            (self.in_neighbours[id].sample_num, self.in_neighbours[id].model)
            for id in neighbour_ids
        ]
        (num0, averaged_params) = model_list[0]
        for k in averaged_params.keys():
            for i in range(0, len(model_list)):
                local_sample_number, local_model_params = model_list[i]
                w = local_sample_number / training_num
                if i == 0:
                    averaged_params[k] = local_model_params[k] * w
                else:
                    averaged_params[k] += local_model_params[k] * w

        return averaged_params

    def sample_clients(self, round_idx, client_num_per_round):
        num_neighbours = len(self.in_neighbours)
        if num_neighbours == client_num_per_round:
            selected_neighbours = [
                neighbour for neighbour in self.in_neighbours]
        else:
            with RandomContext(round_idx):
                selected_neighbours = np.random.choice(
                    self.in_neighbours, min(client_num_per_round, num_neighbours), replace=False)
        logging.info("worker_indexes = %s" % str(selected_neighbours))
        return selected_neighbours

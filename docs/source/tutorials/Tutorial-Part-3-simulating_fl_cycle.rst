Simulating Federated Learning Cycle
===================================

FL Simulation
-------------

Trainers and aggregators are both defined as workers in the simulator.
There are multiple types of computations that each worker performs
based on their assigned role.

It is the role of the orchestrator to define these roles for the workers
and
initialize them.

For the purposes of the simulator, the `train_fl <../train_fl.py>`__ file
behaves as the orchestrator and initiates all the workers.

Federated Worker
----------------

The federated worker class implements all the networking and FL logic.
It's the responsibility of the developer needs to implement three basic methods of the federated worker- aggregation logic, client selection,
and role description.

Worker Roles
~~~~~~~~~~~~

Roles define the kind of computation each worker does.In this tutorial,
we are using the `FedAvg McMahan etal <https://arxiv.org/abs/1602.05629>`__ strategy with random client selection. There are only two roles here
namely, the aggregator and trainer.

-  **Aggregator** requests models from the trainers before aggregating
   and updating its model.
-  **Trainer** responds to aggregators’ requests after updating its own
   model by local training.

We define these roles in the ``run()`` method of Federated Worker.

.. code:: python


   @registry.load('fl_algo', 'fed_avg')
   class FedAvgWorker(FederatedWorker):
       def __init__(self, ...):
           super().__init__(...)

       async def run(self):
           assert role in self.roles, InvalidStateError("unknown role for worker")

           if role == 'aggregator':
               # central server in this case
               neighbours = await self.request_models_suspendable(self.sample_neighbours())
               weighted_params = self.aggregate(neighbours)
               self.update_model(weighted_params)
           elif role == 'trainer':
               aggregators = list(self.out_neighbours.values())
               global_models = await self.request_models_suspendable(aggregators)
               self.update_model(global_models[0])
               await self.train(model_dir=self.persistent_storage)
           self.round_idx += 1

Aggregation Strategy
~~~~~~~~~~~~~~~~~~~~

In the aggregation strategy, the model updates from the trainers are
combined into a single model update. There are different FL strategies
for personalization, parallelization, and accuracy improvement in every
FL paper.

Recent studies propose a second-order aggregation strategy to compensate
for communication losses. We would run the simplest one here - average
them all!

.. code:: python

       # Your aggregation strategy
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

Client Selection
~~~~~~~~~~~~~~~~

This is one of the most crucial stages of the FL cycle. It is necessary
to build a robust client selection strategy. It can save you from
malicious poisoning attacks, biased models, and slow training cycles.

NimbleEdge brings along specific algorithms that augment the client
selection strategy to deal with the above problems.

For now, we just take random selection…

.. code:: python

       # Your sampling strategy
       def sample_neighbours(self, round_idx, client_num_per_round):
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

**Hurray!**

And it’s done. Simply run the `train_fl.py <../train_fl.py>`__ and see
the simulator in action.

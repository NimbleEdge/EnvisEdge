Starting with NimbleEdge
========================

The Simulation
--------------

Before we put a code into production we need to evaluate the models and
run benchmarks to get the expected accuracy gains.

There is a `simulator <https://github.com/NimbleEdge/EnvisEdge>`__
created by NimbleEdge exactly for this purpose.

-  The FL simulator is designed in a way to make the architecture as
   close to real world deployments as possible.
-  You can simulate both the normal ML training and FL training with the
   simulator.
-  The design is scalable to hit 10000+ workers running in the
   simulation.

Let’s take an example of FB AI’s
`DLRM <https://arxiv.org/abs/1906.00091>`__. This is one of the standard
baselines for recommendation engines. We will be training this model on
`Kaggle Criteo Ads
Data <https://www.kaggle.com/c/criteo-display-ad-challenge>`__.

Model Definition
----------------

All the model descriptions go into
`fedrec/modules <https://github.com/NimbleEdge/EnvisEdge/tree/main/fedrec/modules>`__.
You can add your folder of models as well and hook the registry with
it.

We will create a file dlrm.py and write its implementation in standard
PyTorch code.

.. code:: python

   from torch import nn


   class DLRM_Net(nn.Module):
       
       def __init__(self, arg1, arg2, arg3):
           # Your model description comes here.
       
       def forward(inputs):
           # process inputs
           return output

To see the real implementation of DLRM, please check out the `dlrm
implementation in the repository <../fedrec/modules/dlrm.py>`__

Hooking the registry
--------------------

The simulator makes it easy to experiment with different model
architectures, hyper parameters, optimizers and other components of an
ML pipeline.

We define a `registry class <../fedrec/utilities/registry.py>`__ which
records all the model definitions, optimizers and attaches a
configuration file to the top.

For all your experiments simply define the config file and you are done.

In our DLRM model description, we record it in the registry by
annotating it with ``@registry.load(<Class Type>, <Name>)``

.. code:: python

   from torch import nn
   from fedrec.utilities import registry

   @registry.load('model','dlrm')
   class DLRM_Net(nn.Module):
       
       def __init__(self, arg1, arg2, arg3):
           # Your model description comes here.
       
       def forward(inputs):
           # process inputs
           return output

Now create a `config.yml <../configs/dlrm.yml>`__ file to pass the
arguments and hyper parameters.

.. code:: yaml

   model: # The <Class Type> annotated in registry
       name : 'dlrm' # The unique identifier key

Standard Training
-----------------

Training your model in the normal non-FL settting requires you to write
the implementations for ``train`` and ``test`` methods. You can also
implement ``validate`` method if you want and all these methods will
automatically be serialized into FL plans when we move into FL
deployment.

The `BaseTrainer <../fedrec/trainers/base_trainer.py>`__ abstracts away
the basic methods needed to implemented.

Simply subclass the ``BaseTrainer`` and create your own trainer object.
We will call this DLRMTrainer

.. code:: python

   @registry.load('trainer', 'dlrm')
   class DLRMTrainer(BaseTrainer):

       def __init__(
               self,
               config_dict: Dict,
               train_config: DLRMTrainConfig,
               logger: BaseLogger,
               model_preproc: PreProcessor,) -> None:

           self.train_config = train_config
           super().__init__(config_dict, train_config, logger, model_preproc)

Next implement the data loaders. These are standard PyTorch dataloaders
and return them in the Trainer class.

.. code:: python

   @property
   def dataloaders(self):
       return {
               'train': train_data_loader,
               'train_eval': train_eval_data_loader,
               'val': val_data_loader
           }

Define the train and test methods of ``BaseTrainer`` in ``DLRMTrainer``.

With this you are ready to train your model. Till now we have been doing
what you usually do to train your ML models. We have been writing
standard PyTorch code and developing our ML pipeline.

Federated Training
------------------

Now we will simulate DLRM in federated setting. Create data split to
mimic your users. We use Drichlet sampling for creating non-IID datasets
for the model.

Implement your own federated learning algorithm. In the demo we are
using Federated Averaging. You just need to sub-class
`FederatedWorker <fedrec/federated_worker.py>`__ and implement ``run()``
method.

.. code:: python


   @registry.load('fl_algo', 'fed_avg')
   class FedAvgWorker(FederatedWorker):
       def __init__(self, ...):
           super().__init__(...)

       async def run(self):
           '''
               `Run` function updates the local model.
               Implement this method to determine how the roles interact with each other to determine the final updated model.
               For example a worker which has both the `aggregator` and `trainer` roles might first train locally then run discounted `aggregate()` to get the fianl update model


               In the following example,
               1. Aggregator requests models from the trainers before aggregating and updating its model.
               2. Trainer responds to aggregators' requests after updating its own model by local training.

               Since standard FL requires force updates from central entity before each cycle, trainers always start with global model/aggregator's model

           '''
           assert role in self.roles, InvalidStateError("unknown role for worker")

           if role == 'aggregator':
               neighbours = await self.request_models_suspendable(self.sample_neighbours())
               weighted_params = self.aggregate(neighbours)
               self.update_model(weighted_params)
           elif role == 'trainer':
               # central server in this case
               aggregators = list(self.out_neighbours.values())
               global_models = await self.request_models_suspendable(aggregators)
               self.update_model(global_models[0])
               await self.train(model_dir=self.persistent_storage)
           self.round_idx += 1

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

Begin FL simulation by

.. code:: bash

   mpirun -np 20 python -m mpi4py.futures train_fl.py --num_workers 1000.

In the `next section <./Tutorial-Part-3-simulating_fl_cycle.md>`__ we
will see how easy it is to convert the normal ML pipeline into an FL
pipeline.



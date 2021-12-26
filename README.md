
![License](https://img.shields.io/github/license/NimbleEdge/RecoEdge?style=plastic)
![Activity](https://img.shields.io/github/last-commit/NimbleEdge/RecoEdge?style=plastic)
[![Chat on Discord](https://img.shields.io/discord/889803721339445288?color=purple&label=Discord&style=plastic)](https://nimbleedge.ai/discord)

# RecoEdge: Bringing Recommendations to the Edge
A one stop solution to build your recommendation models, train them and, deploy them in a privacy preserving manner-- right on the users' devices. 

RecoEdge integrate the phenomenal works by [OpenMined](https://www.openmined.org/) and [FedML](https://github.com/FedML-AI/FedML) to easily explore new federated learning algorithms and deploy them into production.

The steps to building an awesome recommendation system:
1. :nut_and_bolt: **Standard ML training:** Pick up any ML model and benchmark it using [BaseTrainer](fedrec/trainers/base_trainer.py)
2. :video_game: **Federated Learning Simulation:** Once you are satisfied with your model, explore a host of FL algorithms with [FederatedWorker](fedrec/federated_worker.py)
3. :factory:	**Industrial Deployment:** After all the testing and simulation, deploy easily using [PySyft](https://github.com/openmined/Pysyft) from OpenMined
4. :rocket: **Edge Computing:** Integrate with [NimbleEdge](https://www.nimbleedge.ai/) to improve FL training times by over **100x**.


# QuickStart

Let's train [Facebook AI's DLRM](https://arxiv.org/abs/1906.00091) on the edge. DLRM has been a standard baseline for all neural network based recommendation models.

Clone this repo and change the argument `datafile` in [configs/dlrm.yml](configs/dlrm.yml) to the above path.
```bash
git clone https://github.com/NimbleEdge/RecoEdge
```
```yml
model :
  name : 'dlrm'
  ...
  preproc :
    datafile : "<Path to Criteo>/criteo/train.txt"
 
```
Install the dependencies with conda or pip
```bash
conda env create --name recoedge --file environment.yml
conda activate recoedge
``` 

Run data preprocessing with [preprocess_data](preprocess_data.py) and supply the config file. You should be able to generate per-day split from the entire dataset as well a processed data file
```bash
python preprocess_data.py --config configs/dlrm.yml --logdir $HOME/logs/kaggle_criteo/exp_1
```

**Begin Training**
```bash
python train.py --config configs/dlrm.yml --logdir $HOME/logs/kaggle_criteo/exp_3 --num_eval_batches 1000 --devices 0
```

Run tensorboard to view training loss and validation metrics at [localhost:8888](http://localhost:8888/)
```bash
tensorboard --logdir $HOME/logs/kaggle_criteo --port 8888
```

# Federated Training
_This section is still work in progress. Reach out to us directly if you need help with FL deployment_

Now we will simulate DLRM in federated setting. Create data split to mimic your users. We use Drichlet sampling for creating non-IID datasets for the model.

```bash
```

Adjust the parameters for distributed training like MPI in the [config file](configs/dlrm_fl.yml)
```yaml
communications:
  gpu_map:
    host1: [0, 2]
    host2: [1, 0, 1]
    host3: [1, 1, 0, 1]
    host4: [0, 1, 0, 0, 0, 1, 0, 2]
```

Implement your own federated learning algorithm. In the demo we are using Federated Averaging. You just need to sub-class [FederatedWorker](fedrec/federated_worker.py) and implement `run()` method.

```python

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
```

Begin FL simulation by
```bash
mpirun -np 20 python -m mpi4py.futures train_fl.py --num_workers 1000.
```

Deploy with PySyft
# Customization
## Training Configuration
There are two ways to adjust training hyper-parameters:
- **Set values in config/*.yml** persistent settings which are necessary for reproducibility eg randomization seed
- **Pass them as CLI argument** Good for non-persistent and dynamic settings like gpu device  

*In case of conflict, CLI argument supercedes config file parameter.*
For further reference, check out [training config flags](configs/flags.md)

## Model Architecture
### Adjusting DLRM model params 
Any parameter needed to instantiate the pytorch module can be supplied by simply creating a key-value pair in the config file.

For example DLRM requires `arch_feature_emb_size`, `arch_mlp_bot`, etc 
```yml
model: 
  name : 'dlrm'
  arch_sparse_feature_size : 16
  arch_mlp_bot : [13, 512, 256, 64]
  arch_mlp_top : [367, 256, 1]
  arch_interaction_op : "dot"
  arch_interaction_itself : False
  sigmoid_bot : "relu"
  sigmoid_top : "sigmoid"
  loss_function: "mse"
```

### Adding new models
Model architecture can only be changed via `configs/*.yml` files. Every model declaration is tagged with an appropriate name and loaded into registry.
```python
@registry.load('model','<model_name>')
class My_Model(torch.nn.Module):
    def __init__(num):
        ... 
```

You can define your own modules and add them in the [fedrec/modules](fedrec/modules). Finally set the `name` flag of `model` tag in config file
```yml
model : 
  name : "<model name>"
```

# Contribute

1. Star, fork, and clone the repo.
2. Do your work.
3. Push to your fork.
4. Submit a PR to NimbleEdge/RecoEdge

We welcome you to the [Discord](https://nimbleedge.ai/discord) for queries related to the library and contribution in general.

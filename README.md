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
# Contribute

1. Please go through our [CONTRIBUTING](https://github.com/NimbleEdge/RecoEdge/blob/main/CONTRIBUTING.md) guidelines before starting.
2. Star, fork, and clone the repo.
3. Do your work.
4. Push to your fork.
5. Submit a PR to NimbleEdge/RecoEdge

We welcome you to the [Discord](https://nimbleedge.ai/discord) for queries related to the library and contribution in general.

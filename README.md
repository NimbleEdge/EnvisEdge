<h1 align="center">

  <br>
  <img src="./assets/recoedge-banner-dark.png#gh-light-mode-only" alt="RecoEdge"/ height="140" width="550">
  <img src="./assets/recoedge-banner-light.png#gh-dark-mode-only" alt="RecoEdge"/ height="140" width="550">
  <br>
  Bringing Recommendations to the Edge
  <br>

</h1>
<p align="center">
<a href=""><img src="https://img.shields.io/github/license/NimbleEdge/RecoEdge?style=plastic" alt="Lisence"></a>
<a href=""><img src="https://img.shields.io/github/last-commit/NimbleEdge/RecoEdge?style=plastic" alt="Activity"></a>
<a href="https://nimbleedge.ai/discord"><img src="https://img.shields.io/discord/889803721339445288?color=purple&label=Discord&style=plastic" alt="Discord"></a>
<img src="https://img.shields.io/github/issues/NimbleEdge/RecoEdge?style=plastic&color=blue" alt="OpenIssues">
<a href=""><img src="https://github.com/NimbleEdge/RecoEdge/actions/workflows/codeql-analysis.yml/badge.svg"></a>  

<br>
<br>
<a href="https://github.com/NimbleEdge/RecoEdge/pulse"><img src="./assets/sparkline-banner.png" alt="Sparkline"/ height="50" width="250"></a>
<br>  
</p>

A one-stop solution to build your recommendation models, train them and, deploy them in a privacy-preserving manner-- right on the users' devices.

RecoEdge allows you to easily explore new federated learning algorithms and deploy them into production.

The steps to building an awesome recommendation system are:
1. 🔩 **Standard ML training**: Pick up any ML model and benchmark it using standard settings.
2. 🎮 Federated Learning Simulation: Once you are satisfied with your model, explore a host of FL algorithms with the simulator.
3. 🏭 Industrial Deployment: After all the testing and simulation, deploy easily using NimbleEdge suite
4. 🚀 Edge Computing: Leverage all the benefits of edge computing

# Repo Structure 🏢
  
 ```
NimbleEdge/RecoEdge
├── CONTRIBUTING.md           <-- Please go through the contributing guidelines before starting 🤓
├── README.md                 <-- You are here 📌
├── docs                      <-- Tutorials and walkthroughs 🧐
├── experiments               <-- Recommendation models used by our services
└── fedrec                    <-- Whole magic takes place here 😜 
      ├── communications        <-- Modules for communication interfaces eg. Kafka
      ├── multiprocessing       <-- Modules to run parallel worker jobs
      ├── python_executors      <-- Contains worker modules eg. trainer and aggregator
      ├── serialization         <-- Message serializers
      └── utilities             <-- Helper modules
├── fl_strategies             <-- Federated learning algorithms for our services.
└── notebooks                 <-- Jupyter Notebook examples
``` 
  
# QuickStart

Let's train [Facebook AI's DLRM](https://arxiv.org/abs/1906.00091) on the edge. DLRM has been a standard baseline for all neural network based recommendation models.

Clone this repo and change the argument `datafile` in [configs/dlrm_fl.yml](configs/dlrm_fl.yml) to the above path.
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
Download kafka from [Here](https://github.com/apache/kafka) 👈
and start the kafka server using the following commands

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```
Create kafka topics for the job executor

```bash
bin/kafka-topics.sh --create --topic job-request-aggregator --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic job-request-trainer --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic job-response-aggregator --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --topic job-response-trainer --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

To start the multiprocessing executor run the following command:

```bash
python executor.py --config configs/dlrm_fl.yml
```
Change the path in [Dlrm_fl.yml](https://github.com/NimbleEdge/RecoEdge/blob/740f50e8c367e4824c704d826ea65866cac31664/configs/dlrm_fl.yml#L32) to your data path.
```
preproc :
    datafile : "<Your path to data>/criteo_dataset/train.txt"
```
Run data preprocessing with [preprocess_data](preprocess_data.py) and supply the config file. You should be able to generate per-day split from the entire dataset as well a processed data file
```bash
python preprocess_data.py --config configs/dlrm_fl.yml --logdir $HOME/logs/kaggle_criteo/exp_1
```

**Begin Training**
```bash
python train.py --config configs/dlrm_fl.yml --logdir $HOME/logs/kaggle_criteo/exp_3 --num_eval_batches 1000 --devices 0
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

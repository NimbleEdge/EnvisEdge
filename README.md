<h1 align="center">

  <br>
  <img src="./assets/envisedge-banner-dark.png#gh-light-mode-only" alt="EnvisEdge"/ height="350" width="700">
  <img src="./assets/envisedge-banner-light.png#gh-dark-mode-only" alt="EnvisEdge"/ height="350" width="700">
  <br>
  Experience Edge on Cloud - An Edge Simulator!
  <br>

</h1>
<p align="center">
<a href=""><img src="https://img.shields.io/github/license/NimbleEdge/EnvisEdge?style=plastic" alt="Lisence"></a>
<a href=""><img src="https://img.shields.io/github/last-commit/NimbleEdge/EnvisEdge?style=plastic" alt="Activity"></a>
<a href="https://nimbleedge.ai/discord"><img src="https://img.shields.io/discord/889803721339445288?color=purple&label=Discord&style=plastic" alt="Discord"></a>
<img src="https://img.shields.io/github/issues/NimbleEdge/EnvisEdge?style=plastic&color=blue" alt="OpenIssues">
<a href=""><img src="https://github.com/NimbleEdge/EnvisEdge/actions/workflows/codeql-analysis.yml/badge.svg"></a>  

<br>
<br>
<a href="https://github.com/NimbleEdge/EnvisEdge/pulse"><img src="./assets/sparkline-banner.png" alt="Sparkline"/ height="50" width="250"></a>
<br>  
</p>

EnvisEdge simulates an edge-like experience for you to experiment with edge-related technologies on the cloud. 

For example, it can simulates Federated Learning (FL) environment on cloud for 50-10000 workers. This might be useful for remote teams of data scientists, researchers and developers working on model development that can be tested online first and then deployed to the edge. Or for a research team working on initial concept generation and testing, with limited budget or the difficulty in obtaining the requisite hardware stack.

**Life Stages of your ML Model from creation to Edge deployment:** 
1. 🔩 **Standard ML training**: Take any machine learning model and benchmark it using standard parameters.
2. 🎮 **Federated Learning Simulation**: Once you're happy with your model, use the EnvisEdge to experiment with a variety of FL algorithms.
3. 🏭 **Industrial Deployment**: After all of the testing and simulation, use the NimbleEdge stack to quickly deploy it.
4. 🚀 **Edge Computing**: Leverage all the benefits of edge computing.


### Key features :star2: 
1. Provides a platform for global or remote teams to run and test their models prior to edge deployments.
2. Run, train and test FL models just like in Edge in EnvisEdge Simulation. 
3. Hardware constraints may restrict edge computation. Use EnvisEdge to test your ideas. 

# Repo Structure 🏢
  
 ```
NimbleEdge/EnvisEdge
├── CONTRIBUTING.md           <-- Please go through the contributing guidelines before starting 🤓
├── README.md                 <-- You are here 📌
├── datasets                  <-- Sample datasets
├── docs                      <-- Tutorials and walkthroughs 🧐
├── experiments               <-- Recommendation models used by our services
└── fedrec                    <-- Whole magic takes place here 😜 
      ├── communications          <-- Modules for communication interfaces eg. Kafka
      ├── multiprocessing         <-- Modules to run parallel worker jobs
      ├── python_executors        <-- Contains worker modules eg. trainer and aggregator
      ├── serialization           <-- Message serializers
      └── utilities               <-- Helper modules
├── fl_strategies             <-- Federated learning algorithms for our services.
├── notebooks                 <-- Jupyter Notebook examples
├── scala-core                <-- Scala version of EnvisEdge
├── scripts                   <-- Separate DLRM recommender code  
└── tests                     <-- tests
``` 
  
# QuickStart

Let's train [Facebook AI's DLRM](https://arxiv.org/abs/1906.00091) on the edge. DLRM has been a standard baseline for all neural network based recommendation models.

Clone this repo and change the argument `datafile` in [configs/dlrm_fl.yml](configs/dlrm_fl.yml) to the above path.
```bash
git clone https://github.com/NimbleEdge/EnvisEdge
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
mkdir env
cd env
virtualenv envisedge 
source envisedge/bin/activate 
pip3 install -r requirements.txt
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
Change the path in [Dlrm_fl.yml](configs/dlrm_fl.yml) to your data path.
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
# Demos and Tutorials
You may find all the EnvisEdge related demos and tutorials [here](https://github.com/NimbleEdge/EnvisEdge/tree/refactor-user-module/docs).

You may also find the official documentation [here](https://docs.nimbleedge.ai/).

# Start Contributing

1. Before you begin, please read our [CONTRIBUTOR'S](https://github.com/NimbleEdge/EnvisEdge/blob/main/CONTRIBUTING.md) GUIDELINES.
2. Introduce yourself in the #introduction channel on [Discord](https://nimbleedge.ai/discord) ( Most of the talks and discussions happen here.)
3. Look for an open issue that interests you. Liverage labels feature as shown below
![Label wise issue search](https://github.com/shaistha24/EnvisEdge/blob/main/assets/issues.gif) 
4. Star, fork, and clone the repo. 
5. Get down to business. Do your work.
6. Push to your fork.
7. Send a pull request to NimbleEdge/EnvisEdge.

# License
[Apache License 2.0](https://github.com/NimbleEdge/EnvisEdge/blob/refactor-user-module/LICENSE)


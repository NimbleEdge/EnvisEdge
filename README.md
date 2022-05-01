<h1 align="center">

  <br>
  <img src="./assets/envisedge-banner-dark.png#gh-light-mode-only" alt="EnvisEdge"/ height="350" width="700">
  <img src="./assets/envisedge-banner-light.png#gh-dark-mode-only" alt="EnvisEdge"/ height="350" width="700">
  <br>
  Envision the Edge like never before...
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
 
EnvisEdge allows users to simulate an edge computing environment to test their ideas and models before putting them in place on the edge. It takes care of all the complex stuff such as diversity across operating systems, computation power and communication mediums, allowing you to focus on the idea rather than the setup. 

EnvisEdge allows researchers, developers and data scientists to experiment and test their hypotheses, and produce production-ready code without having direct access to the edge devices. Creating a path for global research and growth in the domains of federated learning and edge computing.


<h1>Key features 🌟</h1>

1. Provides a platform for global or remote teams to run and test their systems/models prior to deployment.
2. Run, train and test FL algorithms and ML models. 
3. Can setup environment of your choice with any arbitrary hardware constraints such as RAM, CPU and more. 
4. Experience Edge on cloud and your devices.
<br>



<h1>Repo Structure 🏢</h1>

  
 ```
NimbleEdge/EnvisEdge
├── CONTRIBUTING.md                         <-- Please go through the contributing guidelines before starting 🤓
├── README.md                               <-- You are here 📌
├── datasets                                <-- Sample datasets
├── docs                                    <-- Tutorials and walkthroughs 🧐
├── experiments                             <-- Recommendation models used by our services
└── fedrec                                  <-- Whole magic takes place here 😜 
      ├── communication_interfaces              <-- Modules for communication interfaces eg. Kafka
      ├── data_models                           <-- All data modules that will be used for communication and thier serializers and  deserializers
      ├── modules                               <-- All the modules related to transformers, embeddings etc.
      ├── multiprocessing                       <-- Modules to run parallel worker jobs
      ├── optimization                          <-- Modules realted to torch optimizers and gradient decesnt etc.
      ├── python_executors                      <-- Contains worker modules eg. trainer and aggregator
      ├── serialization                         <-- serialization interfaces for data models
      ├── user_modules                          <-- Envis modules for wrapping toech modules for users. 
      └── utilities                             <-- Helper modules
├── fl_strategies                           <-- Federated learning algorithms for our services.
├── notebooks                               <-- Jupyter Notebook examples
├── scala-core                              <-- Backbone of EnvisEdge
├── scripts                                 <-- bash scripts for creating and removing kfka topics.
└── tests                                   <-- tests
``` 
    
<h1>QuickStart</h1>

Update the config files of the model (can be found [here](https://github.com/NimbleEdge/EnvisEdge/tree/main/configs)) you are going to use with logging directory:

```yml
log_dir:
  PATH: <path to your logging directory>
```

Download kafka from [Here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.1.0/kafka_2.13-3.1.0.tgz) 👈
and start the kafka server using the following commands

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```
Create kafka topics for the job executor

```bash
cd scripts
$ bash add_topics.sh
Enter path to kafka Directory : <Enter the path to the kafka directory>
kafka url: <Enter the URL on which kafka is listening e.g if you are running it on localhost it would be 127.0.0.1>
Creating Topics...
```
Install the dependencies using virtual environment
```bash
mkdir env
cd env
virtualenv envisedge
source envisedge/bin/activate
pip3 install -r requirements.txt
``` 

Download the federated dataset 

```bash
$ bash download.sh -f
Enter global data path : <Enter the path you want your dataset to be saved>
Enter model : <Enter the config file of the model to update with the dataset path>
Downloading femnist dataset...
```

Run data preprocessing with [preprocess_data](preprocess_data.py) . Form this you will training dataset with with client mapping that would be send to the python workers for training the model.
```bash
python preprocess_data.py --config configs/regression.yml
```

To start the multiprocessing executor run the following command:

```bash
$ python executor.py --config configs/regression.yml
```
To see how traning is done run the following command:
```bash
$ python tests/integration_tests/integration_test.py --config configs/regression.yml
```
<h1>Demos and Tutorials</h1>
You may find all the EnvisEdge related demos and tutorials [here](https://github.com/NimbleEdge/EnvisEdge/tree/refactor-user-module/docs).

You may also find the official documentation [here](https://docs.nimbleedge.ai/).

<h1>Start Contributing</h1>

1. Before you begin, please read our [CONTRIBUTOR'S](https://github.com/NimbleEdge/EnvisEdge/blob/main/CONTRIBUTING.md) GUIDELINES.
2. Introduce yourself in the #introduction channel on [Discord](https://nimbleedge.ai/discord) ( Most of the talks and discussions happen here.)
3. Look for an open issue that interests you such as [good first issue](https://github.com/NimbleEdge/EnvisEdge/labels/good%20first%20issue), [python](https://github.com/NimbleEdge/EnvisEdge/labels/python), [scala](https://github.com/NimbleEdge/EnvisEdge/labels/scala), [documentation](https://github.com/NimbleEdge/EnvisEdge/labels/documentation%20%F0%9F%93%83) and more. Liverage labels feature as shown below
![Label wise issue search](https://github.com/shaistha24/EnvisEdge/blob/main/assets/issues.gif) 
4. Star, fork, and clone the repo. 
5. Get down to business. Do your work.
6. Push to your fork.
7. Send a pull request to NimbleEdge/EnvisEdge.

<h1>License</h1>
[Apache License 2.0](https://github.com/NimbleEdge/EnvisEdge/blob/refactor-user-module/LICENSE)


Installation
============

Let’s train `Facebook AI’s DLRM <https://arxiv.org/abs/1906.00091>`__ on
the edge. DLRM has been a standard baseline for all neural network based
recommendation models.

Clone this repo and change the argument ``datafile`` in
`configs/dlrm_fl.yml <configs/dlrm_fl.yml>`__ to the above path.

.. code:: bash

   git clone https://github.com/NimbleEdge/RecoEdge

.. code:: yml

   model :
     name : 'dlrm'
     ...
     preproc :
       datafile : "<Path to Criteo>/criteo/train.txt"
    

Install the dependencies with conda or pip

.. code:: bash

   conda env create --name recoedge --file environment.yml
   conda activate recoedge

Download kafka from `Here <https://github.com/apache/kafka>`__ 👈 and
start the kafka server using the following commands

.. code:: bash

   bin/zookeeper-server-start.sh config/zookeeper.properties
   bin/kafka-server-start.sh config/server.properties

Create kafka topics for the job executor

.. code:: bash

   bin/kafka-topics.sh --create --topic job-request-aggregator --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   bin/kafka-topics.sh --create --topic job-request-trainer --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   bin/kafka-topics.sh --create --topic job-response-aggregator --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   bin/kafka-topics.sh --create --topic job-response-trainer --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

To start the multiprocessing executor run the following command:

.. code:: bash

   python executor.py --config configs/dlrm_fl.yml

Change the path in `Dlrm_fl.yml <configs/dlrm_fl.yml>`__ to your data
path.

::

   preproc :
       datafile : "<Your path to data>/criteo_dataset/train.txt"

Run data preprocessing with `preprocess_data <preprocess_data.py>`__ and
supply the config file. You should be able to generate per-day split
from the entire dataset as well a processed data file

.. code:: bash

   python preprocess_data.py --config configs/dlrm_fl.yml --logdir $HOME/logs/kaggle_criteo/exp_1

**Begin Training**

.. code:: bash

   python train.py --config configs/dlrm_fl.yml --logdir $HOME/logs/kaggle_criteo/exp_3 --num_eval_batches 1000 --devices 0

Run tensorboard to view training loss and validation metrics at
`localhost:8888 <http://localhost:8888/>`__

.. code:: bash

   tensorboard --logdir $HOME/logs/kaggle_criteo --port 8888
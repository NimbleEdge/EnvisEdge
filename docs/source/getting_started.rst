********************
Getting started with
********************

.. figure:: _static/envisedge-banner-dark.svg
   :alt: EnvisEdge

   EnvisEdge

.. code:: bash

   git clone https://github.com/NimbleEdge/EnvisEdge

.. code:: bash

   cd EnvisEdge

.. code-block:: RST

   NimbleEdge/EnvisEdge
   ├── CONTRIBUTING.md           <-- Please go through the contributing guidelines before starting 🤓
   ├── README.md                 <-- You are here 📌
   ├── docs                      <-- Tutorials and walkthroughs 🧐
   ├── experiments               <-- Recommendation models used by our services
   └── fedrec                    <-- Whole magic takes place here 😜 
         ├── communications          <-- Modules for communication interfaces eg. Kafka
         ├── multiprocessing         <-- Modules to run parallel worker jobs
         ├── python_executors        <-- Contains worker modules eg. trainer and aggregator
         ├── serialization           <-- Message serializers
         └── utilities               <-- Helper modules
   ├── fl_strategies             <-- Federated learning algorithms for our services.
   └── notebooks                 <-- Jupyter Notebook examples


.. code::

   model :
     name : 'dlrm'
     ...
     preproc :
       datafile : "<Path to Criteo>/criteo/train.txt"
    

.. caution::
   You need to have conda or pip installed in your local.

Install the dependencies with conda or pip

.. code:: bash

   conda env create --name envisedge --file environment.yml
   conda activate envisedge

.. caution::
   You need to have Java installed in your local

`Download <https://www.apache.org/dyn/closer.cgi?path=/kafka/3.0.0/kafka_2.13-3.0.0.tgz>`
the latest kafka release.

.. code:: bash

   tar -xzf kafka_`tab`
   cd kafka_`tab`

Start the kafka server using the following commands

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

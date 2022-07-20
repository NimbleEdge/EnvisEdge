Introduction to Federated Learning
==================================

What is Federated Learning?
---------------------------

Before we dive into how you can deploy an FL system, let's go through the
lifecycle of federated learning and set the standard definitions.
`Kairouz et. al. <https://arxiv.org/pdf/1912.04977.pdf>`__ is a
fantastic survey of the current literature on Federated Learning. We
quote them to define Federated Learning.

   **Federated learning**\ * is a machine learning setting where multiple
   entities (*\ `clients <#clients>`__\ *) collaborate in solving a
   machine learning problem, under the coordination of a central server
   or service provider. Each client’s raw data is stored locally and not
   exchanged or transferred; instead, focused updates intended for
   immediate aggregation are used to achieve the learning objective.*


Types of Federated learning
---------------------------

* **Model Centric:**

  When the distributed data is used to improve a central model with
  a goal of delivering better centrally administered models, it is
  known as Model-Centric Federated Learning.In model centric approach
  the development of experimental research is performed in order to
  improve the ML model performance.This process involves selecting
  the best model architecture and training the process from a wide
  range of possibilities.


  Model Centric Federated Learning is further classifid into:

  * **Cross-Device Federated Learning**

    When Federated Learning takes place through suitable federated techniques
    from data across a wide range of devices.

    Typically, Cross-Device FL uses Horizontal Federated Learning or Homogeneous Federated Learning and it
    can be described as a Federated Learning method which uses a dataset which shares the same features but
    are different in samples.

    * So when data sets share the same features but are different in samples.
    * This is also called as Homogeneous Federated Learning.
    * Supervised Learning uses Horizontal datasets.

  * **Cross-Silo Federated Learning**

    Similar to Cross-Device FL, this FL aims to create a more
    centrally sound model.But, instead of a small concentration
    of data, here humongous amounts of data are stored in clusters
    like Hadoop/Spark.

    Here data sets are partitioned Vertically. Let's take a look at Vertical-FL.

    * When the data set has similar samples, but has different feature sets, it is known
      as Vertical-FL.

* **Data-Centric FL:**

  * Data-Centric Federated Learning is where private users can give organisations
    access to build models on their data without sharing it.

  * This concept can be further expanded to a Cloud of Cross-Silo FL, where similar
    strategy could be implemented.

Clients
~~~~~~~

Clients are the devices responsible for training the model on a dataset
hold locally.

Aggregators
~~~~~~~~~~~

Aggregators are responsible for taking model updates from several clients
and generating an averaged model from the submissions. The same device
can behave as both a client and aggregator, as it happens in
decentralized FL.

Neighbours
~~~~~~~~~~

Neighbours in the context of FL are workers (clients/aggregators) who
can send and receive model updates from each other. In the standard
centralized FL setting, every client has only the central server as its
neighbour.

Federated Learning Cycle
------------------------

A horizontal FL cycle consists of 5 steps:

Client selection
~~~~~~~~~~~~~~~~

The client selection process starts with selecting the
participants before training the global model.As part of
its model updates, each aggregator samples a subset of all
of its neighbours. It is not uncommon to have the neighbours
apply for participation first, and then the aggregator decides
who should be accepted.

Model download
~~~~~~~~~~~~~~

The model parameters and execution plans need to be downloaded, if
they have not already been done. Upon acceptance into the cycle,
the workers ask for the necessary information to begin training.

Local training
~~~~~~~~~~~~~~

Based on the data available on the device, each worker runs a
specified number of iterations locally. Model weights are updated
locally and used for inference.

Reporting
~~~~~~~~~

Once all the participants finishes the training process, they
submit their model updates to the aggregator, which begins the
cycle. The aggregator waits until a fraction of accepted devices
report cycle back with their models.The workers often only send
the compressed model weights to reduce the data consumption

Aggregation
~~~~~~~~~~~

The aggregator then averages the model weights to generate the final
global model. It often uses a non-linear combination of these models
to account for their history and communication errors.

Federated Learning in Deployment
--------------------------------

Now let's explore the roles and steps needed to produce the fl
deployment. What will an engineer need to do to deploy these solutions?

Device instrumentation
~~~~~~~~~~~~~~~~~~~~~~

Store relevant data with an expiry date that is necessary for training.
Preprocessing data for future use. Storing user-item interaction matrix
for recommendations, etc

Simulation
~~~~~~~~~~

Prototype model architectures and FL strategies on a dummy data on the cloud
to set the expectations of the architecture.

Federated model training
~~~~~~~~~~~~~~~~~~~~~~~~

Run training procedures for different types of models with different
hyperparameters. In the end, we choose the best ones for aggregation.

Federated model evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Metrics are extracted from the held-out data on the cloud, and the data
distributed on the devices to find the performance.

Deployment
~~~~~~~~~~

Manual quality assurance, live A/B testing and staged rollout. Usually,
the engineer determines this process. It is precisely similar to how a
typically trained model will be deployed.

We will first build a `normal ML
pipeline <./Tutorial-Part-2-starting_with_nimbleedge.rst>`__ and then
convert it into Federated Setting.

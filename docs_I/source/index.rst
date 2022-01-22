.. figure:: ../assets/recoedge-banner-dark.png
   :alt: RecoEdge

   RecoEdge

|Lisence| |Activity| |Discord| |OpenIssues| |image4|

A one-stop solution to build your recommendation models, train them and,
deploy them in a privacy-preserving manner– right on the users’ devices.

RecoEdge allows you to easily explore new federated learning algorithms
and deploy them into production.

The steps to building an awesome recommendation system are: 

* 🔩 **Standard ML training**: Pick up any ML model and benchmark it using standard settings.
* 🎮 **Federated Learning Simulation**: Once you are satisfied with your model, explore a host of FL algorithms with the simulator.
* 🏭 **Industrial Deployment**: After all the testing and simulation, deploy easily using NimbleEdge suite
* 🚀 **Edge Computing**: Leverage all the benefits of edge computing

.. code-block:: RST

   NimbleEdge/RecoEdge
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


.. |Lisence| image:: https://img.shields.io/github/license/NimbleEdge/RecoEdge?style=plastic
.. |Activity| image:: https://img.shields.io/github/last-commit/NimbleEdge/RecoEdge?style=plastic
.. |Discord| image:: https://img.shields.io/discord/889803721339445288?color=purple&label=Discord&style=plastic
   :target: https://nimbleedge.ai/discord
.. |OpenIssues| image:: https://img.shields.io/github/issues/NimbleEdge/RecoEdge?style=plastic&color=blue
.. |image4| image:: https://github.com/NimbleEdge/RecoEdge/actions/workflows/codeql-analysis.yml/badge.svg

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Contents
========

.. toctree::

   installation
   contributing

Developer docs
==============

__ fedrec:
.. toctree::
   :maxdepth: 2
   :caption: Documentation
   
   fedrec/fedrec
   fedrec/fedrec.communications
   fedrec/fedrec.datasets
   fedrec/fedrec.modules
   fedrec/fedrec.multiprocessing
   fedrec/fedrec.optimization
   fedrec/fedrec.serialization
   fedrec/fedrec.utilities.
   fedrec/modules
   
Tutorials
=========

__ Tutorials:

.. toctree::
   :caption: Tutorials
   :titlesonly:

   tutorials/Tutorial-Part-1-introduction_to_fl
   tutorials/Tutorial-Part-2-starting_with_nimbleedge
   tutorials/Tutorial-Part-3-simulating_fl_cycle
   tutorials/Tutorial-Part-4-deployment
   tutorials/Tutorial-Part-5-local_training
   tutorials/Tutorial-Part-6-customization



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Data Processors and Data Loaders
================================

This tutorial is consists of four parts:

1. Data Interfaces
2. Data Loaders
3. Data Samplers
4. Walkthrough using an example

Data Interfaces
---------------
This section describes how to implement a getItem and length for dataset interface.  First, you have to understand what a dataset interface is, and how to implement it using get item and length.

## What is a Dataset Interface.
The purpose of the dataset interface is to provide a mechanism to describe the properties of datasets.  A dataset is composed of a collection of raw data points and describes the data points. The interface is designed in such a way as to allow new features to be added without disrupting current applications that use the dataset interface. Dataset interface give you the access to a collection of data point that you use the getItem to pick a specific data point to work with.

## Using getItem and Length.
This method below is called to fetch a data sample for a given key, if there is a specific data you need to fetch from the dataset Interface then this would work for you.

fun getItem(index: Int): List<IValue>
Using ‘val length:Int’ method you are calling the method to return the size of the dataset and overriding it as well.

.. code:: kotlin

interface Dataset {
  
    val length: Int
    fun getItem(index: Int): List<IValue>
}


Data Loaders
------------

In this section we will discuss how to use the data loaders to load and
iterate through a dataset.

#. Dataloader
#. Dataloader-iterators


DataLoader
------------

This is the base class that defines the implementation of all DataLoaders.
It’s an integral part of handling the entire Extract Transform Load (ETL) pipeline process of a dataset. It is an Iteratable object(dataset)

    * reset(): this resets its content every time it is called.

.. code:: kotlin

        interface DataLoader : Iterable<List<IValue>> {

            fun reset() {}

        }



Dataloader-iterator
-------------------

It’s used to load that dataset in samples and chunks.

    * dataLoader: this input is used to define the loading and sampling process of a particular dataset
    * next(): this uses uses a specified index range to fetch and load data in chunks
    * hasNext(): this checks if the current index exists in the range of the dataset and returns true if there the current index is less than the length of the dataset otherwise false.



.. code:: kotlin

        class DataLoaderIterator(private val dataLoader: SyftDataLoader) : Iterator<List<IValue>> {

            private val indexSampler = dataLoader.indexSampler

            private var currentIndex = 0

            override fun next(): List<IValue> {
                val indices = indexSampler.indices
                currentIndex += indices.size
                return dataLoader.fetch(indices)
            }

            override fun hasNext(): Boolean = currentIndex < dataLoader.dataset.length

            fun reset() {
                currentIndex = 0
            }

        }



Data Samplers
-------------

In this section we will discuss how to use the data samplers to create a
dataset of a fixed size. We will walk through the following various types of data samplers like:

#. Sampler
#. Batch Sampler
#. Random Sampler
#. Sequential Sampler

Sampler
~~~~~~~~

It’s the base for all Samplers. Whenever we create a sampler or a subclass of sampler, we need to provide two methods named Indices and length

    * Indices: it provides a way to iterate over indices of dataset elements.
    * Length: It returns the length of the returned iterators.

.. code:: kotlin

        interface Sampler {

            val indices: List<Int>
            val length: Int
        }


Batch Samplers
~~~~~~~~~~~~~~~~

As the name suggests Batch, It process the samplers in a batch or group. It wraps another sampler to yield a mini-batch of indices. It has three properties:

    * indexer- It’s a base sampler which can be any iterable object.
    * batchSize - The Size of mini-batch
    * dropLast - If its value is True and the size would less than batchSize then the sampler will drop the last batch.

.. code:: kotlin

        class BatchSampler(
            private val indexer: Sampler,
            private val batchSize: Int = 1,
            private val dropLast: Boolean = false
        ) : Sampler {

            private val mIndices = indexer.indices

            private var currentIndex = 0

            override val indices: List<Int>
                get() = when {
                    currentIndex + batchSize < mIndices.size -> {
                        val batch = mIndices.slice(currentIndex until currentIndex + batchSize)
                        currentIndex += batch.size
                        batch
                    }
                    else -> {
                        if (dropLast) {
                            emptyList()
                        } else {
                            val batch = mIndices.drop(currentIndex)
                            currentIndex = mIndices.size
                            batch
                        }
                    }
                }

            override val length: Int = if (dropLast) floor(1.0 * indexer.length / batchSize).toInt()
                else ceil(1.0 * indexer.length / batchSize).toInt()

            fun reset() {
                currentIndex = 0
            }
        }


Random Samplers
~~~~~~~~~~~~~~~~

As the name suggests, It samples the elements randomly. It has two main components. A user can opt for with or without the replacements.

    * Without replacements: It samples from a shuffled dataset.
    * With replacements: It gives the user a bit more control on what portion you need to select. The user can specify the num_samples to draw from the dataset.
    * dataset: It’s a property of the class.

.. code:: kotlin

    class RandomSampler(private val dataset: Dataset) :
        Sampler {

        override val indices = List(dataset.length) { it }.shuffled()

        override val length: Int = dataset.length

    }

Sequential Samplers:
~~~~~~~~~~~~~~~~~~~~

As the name suggests, it samples the elements sequentially and always in the same order. It also has a property named dataset:

    * dataset: It’s the source from where we can sample the elements.

.. code:: kotlin

        class SequentialSampler(private val dataset: Dataset) :
            Sampler {

            override val indices = List(dataset.length) { it }

            override val length: Int = dataset.length

        }





Walkthrough using an example
----------------------------

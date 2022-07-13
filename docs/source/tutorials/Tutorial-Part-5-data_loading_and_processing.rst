Data Processors and Data Loaders
================================

This tutorial consists of four parts:

1. Data Interfaces
2. Data Loaders
3. Data Samplers
4. Walkthrough using an example

Data Interfaces
---------------

This section describes how to implement a get Item and length for the dataset interface. First, you have to understand what it is, and how to implement it using get item and length.

The dataset interface is to provide a mechanism to describe the properties of datasets. It is composed of a collection of raw data points and describes the data points. It is designed in such a way as to allow new features to be added without disrupting current applications that use the dataset interface. It gives you access to a collection of data points that you use the getItem to pick a specific data point to work with.
  
  * **length** : It describes the length of the dataset.
  * **getItem()** : It fetches a data sample for a given key. 

.. code:: kotlin

    interface Dataset {

        val length: Int
        fun getItem(index: Int): List<IValue>
    }


Data Loaders
------------

In this section, we will discuss how to use the data loaders to load and iterate through a dataset.

#. Dataloader
#. Dataloader-iterators


DataLoader
~~~~~~~~~~

This is the base class that defines the implementation of all DataLoaders.
It’s an integral part of handling the entire Extract Transform Load (ETL) pipeline process of a dataset. It is an Iteratable object(dataset)

    * **reset()** : this resets its content every time it is called.

.. code:: kotlin

        interface DataLoader : Iterable<List<IValue>> {

            fun reset() {}

        }



Dataloader-iterator
~~~~~~~~~~~~~~~~~~~

It’s used to load that dataset in samples and chunks.

    * **dataLoader** : this input is used to define the loading and sampling process of a particular dataset
    * **next()** : this uses a specified index range to fetch and load data in chunks
    * **hasNext()** : this checks if the current index exists in the range of the dataset and returns true if there the current index is less than the length of the dataset otherwise false.



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

In this section, we will discuss how to use the data samplers to create a
dataset of a fixed size. We will walk through the following various types of data samplers:

#. Sampler
#. Batch Sampler
#. Random Sampler
#. Sequential Sampler

Sampler
~~~~~~~~

It’s the base for all Samplers. Whenever we create a sampler or a subclass of the sampler, we need to provide two methods named Indices and length

    * **Indices** : it provides a way to iterate over indices of dataset elements.
    * **Length** : It returns the length of the returned iterators.

.. code:: kotlin

        interface Sampler {

            val indices: List<Int>
            val length: Int
        }


Batch Samplers
~~~~~~~~~~~~~~~~

As the name suggests Batch, It processes the samplers in a batch or group and it wraps another sampler to yield a mini-batch of indices. It has three properties:

    * **indexer** - It’s a base sampler that can be any iterable object.
    * **batchSize** - The Size of mini-batch
    * **dropLast** - If its value is True and the size would be less than batchSize then the sampler will drop the last batch.

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

Random Samplers samples the elements randomly. It consists of two main components in which a user can opt for with or without the replacements.

    * **Without replacements** : It samples from a shuffled dataset.
    * **With replacements** : It gives the user a bit more control on what portion you need to select. The user can specify the num_samples to draw from the dataset.
    * **dataset()** : It’s a property of the class.

.. code:: kotlin

    class RandomSampler(private val dataset: Dataset) :
        Sampler {

        override val indices = List(dataset.length) { it }.shuffled()

        override val length: Int = dataset.length

    }

Sequential Samplers:
~~~~~~~~~~~~~~~~~~~~

In sequential samplers, the elements are sampled sequentially and always in the same order. It also has a property named dataset:

    * **dataset** : It’s the source from where we can sample the elements.

.. code:: kotlin

        class SequentialSampler(private val dataset: Dataset) :
            Sampler {

            override val indices = List(dataset.length) { it }

            override val length: Int = dataset.length

        }





Walkthrough using an example
----------------------------

This tutorial explains the class MNISTDataset. The use of the MNIST Dataset is to create an object of it and use it to pass further into the dataLoader object. The MNIST class implements Dataset Interface and its primary constructor asks for a Resources object. First, we have to specify the ``FEATURESIZE`` and ``DATASET_LENGTH as global constant variables.

Step 1: Define Methods 
* returnDataLoader()
* returnLabelReader() 

.. code:: kotlin

  private fun returnDataReader() = BufferedReader(
        InputStreamReader(
            resources.openRawResource(R.raw.pixels)
        )
    )

    private fun returnLabelReader() = BufferedReader(
        InputStreamReader(
            resources.openRawResource(R.raw.labels)
        )
    )

These methods will be used for instantiating ``trainDataReader`` and ``labelDataReader`` variables by using the resources object

Step 2: Defining necessary variables

Defining variables listed below 

.. code:: kotlin

    private var trainDataReader = returnDataReader()
    private var labelDataReader = returnLabelReader()
    private val oneHotMap = HashMap<Int, List<Float>>()
    private val trainInput = arrayListOf<List<Float>>()
    private val labels = arrayListOf<List<Float>>()

Step 3: ``restartReader()``method 

This method kills the initialized ``trainDataReader`` and ``labelDataReader`` and creates new instances of both the variables

.. code:: kotlin

   private fun restartReader() {
        trainDataReader.close()
        labelDataReader.close()
        trainDataReader = returnDataReader()
        labelDataReader = returnLabelReader()
    }

Step 4: ``readLine()`` method

This method takes nothing and returns a Pair Object which is a pair of two Lists by reading the dataset. This method will be used to create a sample object.

.. code:: kotlin

    private fun readLine(): Pair<List<String>, List<String>> {
            var x = trainDataReader.readLine()?.split(",")
            var y = labelDataReader.readLine()?.split(",")
            if (x == null || y == null) {
                restartReader()
                x = trainDataReader.readLine()?.split(",")
                y = labelDataReader.readLine()?.split(",")
            }
            if (x == null || y == null)
                throw Exception("cannot read from dataset file")
            return Pair(x, y)
        }

Step 5: Defining ``ReadSample()`` and ``ReadAllData()`` methods

First, we will create the ReadSample method which just takes two arraylists of type ``List<Float>as parameters (trainInput, labels)`` and then simply fills the two arraylists taken as parameters by using a sample variable which is defined using ``readLine()``. As this method does this job once we need another method to call this method n number of times so we will create another method called ``ReadAllData()``.
This method simply just calls  ``ReadSample()`` the times of Dataset length defined as constant at starting of the program.

.. code:: kotlin 

      private fun readSample(
              trainInput: ArrayList<List<Float>>,
              labels: ArrayList<List<Float>>
          ) {
              val sample = readLine()

              trainInput.add(
                  sample.first.map { it.trim().toFloat() }
              )
              labels.add(
                  sample.second.map { it.trim().toFloat() }
              )
          }

          private fun readAllData() {
              for (i in 0 until DATASET_LENGTH)
                  readSample(trainInput, labels)
          }

Step 6: Init {}

Inside the ``init {}`` we will fill up the oneHotMap HashMap conditionally based on index values and just call the ReadAllData() method

.. code:: kotlin

    init {
            (0..9).forEach { i ->
                oneHotMap[i] = List(10) { idx ->
                    if (idx == i)
                        1.0f
                    else
                        0.0f
                }
            }

            readAllData()
        }

Step 7: ``getItem()`` method and length variable

We are implementing the ``getItem()`` method and length variable from the Dataset class. The ``getItem()`` method will be used outside the class once we create an object of the ``MNISTDataset class``. In the definition of the ``getItem()`` method it takes in the index number and returns a list of ``IValue Objects``. The ``Ivalue`` is nothing but a locator value that describes a certain location taken in memory. The length variable stores the length of training inputs.

.. code:: kotlin

    override val length: Int = trainInput.size

    override fun getItem(index: Int): List<IValue> {
        val trainingData = IValue.from(
            Tensor.fromBlob(
                trainInput[index].toFloatArray(),
                longArrayOf(1, FEATURESIZE.toLong())
            )
        )

        val trainingLabel = IValue.from(
            Tensor.fromBlob(
                labels[index].toFloatArray(),
                longArrayOf(1, 10)
            )
        )

        return listOf(trainingData, trainingLabel)
    }

Step 8: End-part

Read the whole dataset accordingly.

.. code:: kotlin


      private fun readAllData() {
          for (i in 0 until DATASET_LENGTH)
              readSample(trainInput, labels)
      }

      private fun readSample(
          trainInput: ArrayList<List<Float>>,
          labels: ArrayList<List<Float>>
      ) {
          val sample = readLine()

          trainInput.add(
              sample.first.map { it.trim().toFloat() }
          )
          labels.add(
              sample.second.map { it.trim().toFloat() }
          )
      }


    private fun readLine(): Pair<List<String>, List<String>> {
        var x = trainDataReader.readLine()?.split(",")
        var y = labelDataReader.readLine()?.split(",")
        if (x == null || y == null) {
            restartReader()
            x = trainDataReader.readLine()?.split(",")
            y = labelDataReader.readLine()?.split(",")
        }
        if (x == null || y == null)
            throw Exception("cannot read from dataset file")
        return Pair(x, y)
    }

    private fun restartReader() {
        trainDataReader.close()
        labelDataReader.close()
        trainDataReader = returnDataReader()
        labelDataReader = returnLabelReader()
    }

    private fun returnDataReader() = BufferedReader(
        InputStreamReader(
            resources.openRawResource(R.raw.pixels)
        )
    )

    private fun returnLabelReader() = BufferedReader(
        InputStreamReader(
            resources.openRawResource(R.raw.labels)
        )
    )

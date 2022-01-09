
- [On-device Training](#on-device-training)
  - [Creating the worker job](#creating-the-worker-job)
  - [Training hooks](#training-hooks)
  - [Running the training job](#running-the-training-job)

# On-device Training
In this example we will train our machine learning models on an android device. 

We will import the Device side sdk in our application to take care of managing the FL cycle and interacting with the orchestrator for us.

Create a android project and add the gradle dependency.

In your viewmodel for tha activity implement the listeners to the local on-device worker.

```Kotlin
    // Optional: Make an http request to your server to get an authentication token
    val authToken = apiClient.requestToken("https://www.mywebsite.com/request-token/$userId")

    // The config defines all the adjustable properties of the worker
    // The url entered here cannot define connection protocol like https/wss since the worker allots them by its own
    // `this` supplies the context. It can be an activity context, a service context, or an application context.
    val config = Configuration.builder(this, "www.my-orchestrator-url.com").build()

    // Initiate the worker to handle all your jobs
    val worker = Worker.getInstance(authToken, configuration)

```
## Creating the worker job

To create a training job locally, you need to supply the exact names for the model that is hosted on the orchestrator otherwise the cycle will fail at authentication.

```kotlin
// Create a new training job
val job = worker.newJob("dlrm", "1.0.0")
```

## Training hooks

There are three hooks that need to implemented on the app side:
1. `onReady()` This is called when the worker has downloaded all the necessary parameters and hyper-params to begin the training process. You should implement all the training logic here.
2. `onRejected()` If the device could pass the selction criteria of the aggregator it responds with the time to try again. The worker shoudl wait for the given time period before requesting for participation again.
3. `onError()` In case any error happens during the execution, this callback is executed. As a fallback we can implement cloud connectivity here or simply log the message and send to the server.

```Kotlin
// Define training procedure for the job
    val jobStatusSubscriber = object : JobStatusSubscriber() {
        override fun onReady(
            model: Model,
            plans: ConcurrentHashMap<String, Plan>,
            clientConfig: ClientConfig
        ) {
            // This function is called when the worker has downloaded the plans and protocols from Orchestrator
            // You are ready to train your model on your data
            // param model stores the model weights given by the server
            // param plans is a HashMap of all the planIDs and their plans.
            // ClientConfig has hyper parameters like batchsize, learning rate, number of steps, etc

            // Plans are accessible by their plan Id used while hosting them.

            repeat(clientConfig.properties.maxUpdates) { step ->

                // get relevant hyperparams from ClientConfig.planArgs
                // All the planArgs will be string and it is upon the user to deserialize them into correct type
                val batchSize = (clientConfig.planArgs["batch_size"]
                                 ?: error("batch_size doesn't exist")).toInt()
                val batchIValue = IValue.from(
                    Tensor.fromBlob(longArrayOf(batchSize.toLong()), longArrayOf(1))
                )
                val lr = IValue.from(
                    Tensor.fromBlob(
                        floatArrayOf(
                            (clientConfig.planArgs["lr"] ?: error("lr doesn't exist")).toFloat()
                        ),
                        longArrayOf(1)
                    )
                )
                // your custom implementation to read a databatch from your data
                val batchData = dataRepository.loadDataBatch(clientConfig.batchSize)
                //get Model weights and return if not set already
                val modelParams = model.getParamArray() ?: return
                val paramIValue = IValue.listFrom(*modelParams)
                // plan.execute runs a single gradient step and returns the output as PyTorch IValue
                val output = plan.execute(
                    batchData.first,
                    batchData.second,
                    batchIValue,
                    lr,paramIValue
                )?.toTuple()
                // The output is a tuple with outputs defined by the plan along with all the model params
                output?.let { outputResult ->
                    val paramSize = model.modelState!!.syftTensors.size
                    // The model params are always appended at the end of the output tuple
                    val beginIndex = outputResult.size - paramSize
                    val updatedParams =
                            outputResult.slice(beginIndex until outputResult.size)
                    // update your model. You can perform any arbitrary computation and checkpoint creation with these model weights
                    model.updateModel(updatedParams.map { it.toTensor() })
                    // get the required loss, accuracy, etc values just like you do in Pytorch Android
                    val accuracy = outputResult[0].toTensor().dataAsFloatArray.last()
                }
            }
            // Once training finishes generate the model diff
            val diff = job.createDiff()
            // Report the diff to finish the cycle
            job.report(diff)
        }

        override fun onRejected() {
        // Implement this function to define what your worker will do when your worker is rejected from the cycle
        }

        override fun onError(throwable: Throwable) {
        // Implement this function to handle error during job execution
        }
    }
```

## Running the training job

Once all the on-device training pipelines have been implemented, you can simply call `start()` to begin the training.

```kotlin
job.start()
```

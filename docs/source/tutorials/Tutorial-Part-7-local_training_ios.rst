Local Training on iOS
=====================

In this example, we will train our machine learning models and we will also learn how to use NimbleEdge SDK to train a plan with local data on an iOS device.

We will import the device SDK into our application to take care of managing the FL cycle, Create an ios project and add the cocoa dependency.

We will create a new client using a cloud aggregating service URL. This client is stored as a property to prevent it from delocating during the training.

.. code:: Swift

    let authToken = /* Get auth token from somewhere (if auth is required): */
    if let syftClient = SyftClient(url: URL(string: "ws://127.0.0.1:5000")!, authToken: authToken) {
    self.syftClient = syftClient

Creating new job
~~~~~~~~~~~~~~~~
To create a training job locally, you need to supply the model name and version.

.. code:: Swift

    self.syftJob = syftClient.newJob(modelName: "mnist", version: "1.0.0")

Training Hooks
~~~~~~~~~~~~~~
Here is a function called onReady( ) that's called when NimbleEdge SDK has downloaded plans, and parameters from the cloud aggregating service and is ready to train the model on your data.The function onReady( )
consists of four parameters where modelParams contains the tensor parameters of your model and update these tensors during training in order to generate the diff at the end of your training run. Plans contain all code information to execute on the devices. 
ClientConfig contains the configuration for the training cycle and metadata for the model. ModelReport is used as a complete block and reports the diff to the cloud aggregating service.


.. code:: Swift

    self.syftJob?.onReady(execute: { modelParams, plans, clientConfig, modelReport in
    guard let MNISTDataAndLabelTensors = try? MNISTLoader.loadAsTensors(setType: .train) else {
        return
    }

    let dataLoader = MultiTensorDataLoader(dataset: MNISTDataAndLabelTensors, shuffle: true, batchSize: 64)

    for batchedTensors in dataLoader {
      autoreleasepool {
          let MNISTTensors = batchedTensors[0].reshape([-1, 784])
          let labels = batchedTensors[1]
          let batchSize = [UInt32(clientConfig.batchSize)]
          let learningRate = [clientConfig.learningRate]

          guard
              let batchSizeTensor = TorchTensor.new(array: batchSize, size: [1]),
              let learningRateTensor = TorchTensor.new(array: learningRate, size: [1]) ,
              let modelParamTensors = modelParams.paramTensorsForTraining else
          {
              return
          }

Execution of plan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The plan is executed using the training and validation dataset and hyperparameters such as batch size, the learning rate, and model parameters.

.. code:: Swift

          let result = plans["training_plan"]?.forward([TorchIValue.new(with: MNISTTensors),
                                                        TorchIValue.new(with: labels),
                                                        TorchIValue.new(with: batchSizeTensor),
                                                        TorchIValue.new(with: learningRateTensor),
                                                        TorchIValue.new(withTensorList: modelParamTensors)])
          guard let tensorResults = result?.tupleToTensorList() else {
              return
          }

List of returned Tensors
~~~~~~~~~~~~~~~~~~~~~~~~
From the above example, the list of tensors is returned in the following order - loss, accuracy, and updated model parameters that are sent back to the cloud aggregating service for aggregation.

.. code:: Swift

          let lossTensor = tensorResults[0]
          lossTensor.print()
          let loss = lossTensor.item()

          let accuracyTensor = tensorResults[1]
          accuracyTensor.print()

          // Get updated param tensors and update them in param tensors holder
          let param1 = tensorResults[2]
          let param2 = tensorResults[3]
          let param3 = tensorResults[4]
          let param4 = tensorResults[5]

          modelParams.paramTensorsForTraining = [param1, param2, param3, param4]

      }
    }

        let diffStateData = try plan.generateDiffData()
        modelReport(diffStateData)

  })

Error Handlers
~~~~~~~~~~~~~~
Here are two error handlers that get implemented on specific conditions: 1. onError( ) This is the error handler for any job execution errors like failure to connect a cloud aggregating service. 2. onRejected( ) If you are being rejected from participating in the training cycle this error handler comes into play where you can retry again after the suggested timeout.

.. code:: Swift

      self.syftJob?.onError(execute: { error in
      print(error)
      })

      self.syftJob?.onRejected(execute: { timeout in
      if let timeout = timeout {
          // Retry again after timeout
          print(timeout)
      }
   })



Starting the training job
~~~~~~~~~~~~~~~~~~~~~~~~~
At this point, you are ready to start the job and you can even add some specifications as parameters like the job should only execute if the device is being charged with a proper wifi connection. Point to be noted - These options are on by default if you don’t specify them.

.. code:: Swift

       self.syftJob?.start(chargeDetection: true, wifiDetection: true)
    }

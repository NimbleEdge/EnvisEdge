package org.nimbleedge.envisedge

import models._
import messages._
import scala.concurrent.duration._
import scala.collection.mutable.{Map => MutableMap}

import akka.actor.Actor
import akka.actor.Cancellable
import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop
import akka.actor.Timers
import akka.actor.typed.scaladsl.TimerScheduler

object Aggregator {
    def apply(aggId: AggregatorIdentifier, parent: ActorRef[Orchestrator.Command], routerRef: ActorRef[LocalRouter.Command]): Behavior[Command] =
        Behaviors.setup{context =>
            Behaviors.withTimers { timers =>
                new Aggregator(context, timers, aggId, parent, routerRef)
            }
        }
    
    trait Command

    // In case of any Trainer / Aggregator (Child) Termination
    private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
        extends Aggregator.Command
    
    private final case class TrainerTerminated(actor: ActorRef[Trainer.Command], traId: TrainerIdentifier)
        extends Aggregator.Command

    final case class InitiateSampling(samplingPolicy: String) extends Aggregator.Command
    private final case class StartAggregation(aggregationPolicy: String) extends Aggregator.Command

    final case class CheckS3ForModels() extends Aggregator.Command

    private case object TimerKey

    // TODO
    // Add messages here
}

// TODO: parent should be either of orchestrator or aggregator.
class Aggregator(context: ActorContext[Aggregator.Command], timers: TimerScheduler[Aggregator.Command], aggId: AggregatorIdentifier, parent: ActorRef[Orchestrator.Command], routerRef: ActorRef[LocalRouter.Command]) extends AbstractBehavior[Aggregator.Command](context) {
    import Aggregator._
    import FLSystemManager.{ RequestTrainer, TrainerRegistered, RequestAggregator, AggregatorRegistered, RequestRealTimeGraph, StartCycle, KafkaResponse }
    import LocalRouter.RegisterAggregator
    import ConfigManager.{AGGR_SAMPLING_REQUEST_TOPIC,  AGGR_AGGREGATION_REQUEST_TOPIC}


    // TODO
    // Add state and persistent information

    // List of Aggregators which are children of this aggregator
    var aggregatorIdsToRef : MutableMap[AggregatorIdentifier, ActorRef[Aggregator.Command]] = MutableMap.empty

    // List of trainers which are children of this aggregator
    var trainerIdsToRef : MutableMap[TrainerIdentifier, ActorRef[Trainer.Command]] = MutableMap.empty


    routerRef ! RegisterAggregator(aggId.toString(), context.self)

    private var round_index = 0

    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), s"models/${aggId.toString()}/")
    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), s"clients/${aggId.toString()}/")

    context.log.info("Aggregator {} started", aggId.toString())

    def getTrainerRef(trainerId: TrainerIdentifier): ActorRef[Trainer.Command] = {
        trainerIdsToRef.get(trainerId) match {
            case Some(actorRef) =>
                // Need to check whether the trainer parent is valid or not using aggId 
                actorRef
            case None =>
                context.log.info("Creating new Trainer actor for {}", trainerId.toString())
                val actorRef = context.spawn(Trainer(trainerId), s"trainer-${trainerId.name()}")
                context.watchWith(actorRef, TrainerTerminated(actorRef, trainerId))
                trainerIdsToRef += trainerId -> actorRef
                actorRef
        }
    }
        
    def getAggregatorRef(aggregatorId: AggregatorIdentifier): ActorRef[Aggregator.Command] = {
        aggregatorIdsToRef.get(aggregatorId) match {
            case Some(actorRef) =>
                actorRef
            case None =>
                context.log.info("Creating new Aggregator actor for {}", aggregatorId.toString())
                val actorRef = context.spawn(Aggregator(aggregatorId, parent, routerRef), s"aggregator-${aggregatorId.name()}")
                context.watchWith(actorRef, AggregatorTerminated(actorRef, aggregatorId))
                aggregatorIdsToRef += aggregatorId -> actorRef
                actorRef
        }
    }

    def getTrainerHistory() : MutableMap[TrainerIdentifier,TrainerHistory] = {
        // This map will contain all trainers history throughout. 
        // Not specific to one FL cycle.
        // will be stored and retrieved from AWS-S3
        
        var trainerHistoryToRef : MutableMap[TrainerIdentifier, TrainerHistory] = MutableMap.empty
        
        // TODO
        // Retrieve history here from S3
        // This variable will be global and will be saved to S3 db when FL cycle completes
        var globalTrainerHistory : MutableMap[TrainerIdentifier, TrainerHistory] = MutableMap.empty

        for ((key, value) <- trainerIdsToRef) {
            if (globalTrainerHistory.contains(key)) {
                trainerHistoryToRef += key->globalTrainerHistory(key) 
            } else {
                globalTrainerHistory += key -> TrainerHistory(numCompletedFLCycle =0 ,numParticipatedFLCycle = 1, modelMerged = MutableMap.empty)
                trainerHistoryToRef += key -> TrainerHistory(numCompletedFLCycle =0 ,numParticipatedFLCycle = 1, modelMerged = MutableMap.empty)
            }
        }

        return trainerHistoryToRef
    }

    def makeSamplingJobSubmit(clientList: List[String]) : JobSubmitMessage = {
        println("In make Sampling message")
        println(trainerIdsToRef)
        var samplingMessage = JobSubmitMessage (
            __type__ = "fedrec.data_models.job_submit_model.JobSubmitMessage",
            __data__ = JobSubmitMessageData (
                job_args = clientList,
                job_kwargs = null,
                workerstate = null,
                senderid = aggId.name(),
                receiverid = aggId.name(),
                job_type = "sampling"
            )
        )
        return samplingMessage
    }

    def makeAggregationJobSubmit() : JobSubmitMessage = {
        println("In make Aggregation message")
        var aggregationMessage = JobSubmitMessage (
            __type__ = "fedrec.data_models.job_submit_model.JobSubmitMessage",
            __data__ = JobSubmitMessageData (
                job_args = List(),
                job_kwargs = null,
                senderid = aggId.name(),
                receiverid = aggId.name(), // confirm this
                job_type = "aggregate",
                workerstate = WorkerState (
                    __type__ = "fedrec.data_models.aggregator_state_model.AggregatorState",
                    __data__ = WorkerStateData (
                        worker_index = aggId.name(),
                        round_index = round_index,
                        model_prepoc = null,
                        storage = s"/models/${aggId.toString()}/model_file-${round_index-1}.pt", // Confirm this
                        local_sample_number = 0,
                        local_training_steps = 0,
                        state_dict = StateDict (
                            step = 0,
                            model = StateDictModel (
                                __type__ = "fedrec.data_models.state_tensors_model.StateTensors",
                                __data__ = StateDictModelData (
                                    storage = s"/models/${aggId.toString()}/model_file-${round_index-1}.pt" // configure this 
                                )
                            ),
                            worker_state = SubWorkerState (
                                model = SubWorkerStateModel (
                                    __type__ = "experiments.regression.net.Regression_Net",
                                    __data__ = SubWorkerStateModelData (
                                        class_ref_name = "experiments.regression.net.Regression_Net",
                                        state = SubWorkerStateModelDataState (
                                            __type__ = "fedrec.data_models.tensors_model.EnvisTensors",
                                            __data__ = SubWorkerStateModelDataStateData (
                                                tensor_path = s"/models/${aggId.toString()}/model_file-${round_index}.pt" // configure this
                                            )
                                        )
                                    )
                                ),
                                in_neighbours = Map(
                                    "0" -> Neighbour(
                                        "fedrec.data_models.aggregator_state_model.Neighbour",
                                        NeighbourData(
                                            "0",
                                            2,
                                            2,
                                            NeighbourDataModelState(
                                                "fedrec.data_models.state_tensors_model.StateTensors",
                                                NeighbourDataModelStateData(
                                                    s"/clients/${aggId.toString}/0_${round_index}_trainer41.pt"
                                                )
                                            )
                                        )
                                    ),
                                    "1" -> Neighbour(
                                        "fedrec.data_models.aggregator_state_model.Neighbour",
                                        NeighbourData(
                                            "1",
                                            2,
                                            2,
                                            NeighbourDataModelState(
                                                "fedrec.data_models.state_tensors_model.StateTensors",
                                                NeighbourDataModelStateData(
                                                    s"/clients/${aggId.toString}/1_${round_index}_trainer41.pt"
                                                )
                                            )
                                        )
                                    ),

                                ), // Initialize this
                                out_neighbours = Map()
                            )
                        )
                    )
                )
            )
        )
        return aggregationMessage
    }

    override def onMessage(msg: Command): Behavior[Command] =

        msg match {
            case trackMsg @ RequestTrainer(requestId, trainerId, replyTo) =>
                val aggList = trainerId.getAggregators()
                if (aggList.find(x => {aggId == x}) == None) {
                    context.log.info("Aggregator id {} not found in {}", aggId.name(), trainerId.toString())
                } else {
                    // Check if the current aggregator is actually parent of trainer
                    if (trainerId.parentIdentifier == aggId) {
                        val actorRef = getTrainerRef(trainerId)
                        replyTo ! TrainerRegistered(requestId, actorRef)
                    } else {
                        // Getting the next aggregator to send the message to
                        val childAggIndex = aggList.indexOf(aggId)+1
                        val childAgg = aggList(childAggIndex)
                        val aggRef = getAggregatorRef(childAgg)
                        aggRef ! trackMsg
                    }
                }
                this

            case trackMsg @ RequestAggregator(requestId, aggregatorId , replyTo) =>

                // Special case of aggregatorId being equal to currentId
                if (aggregatorId == aggId) {
                    context.log.info("Aggregator id {} is same as current one", aggregatorId.toString())
                } else {
                    val aggList = aggregatorId.getAggregators()
                    if (aggList.find(x => {aggId == x}) == None) {
                        context.log.info("Aggregator id {} not found in {}", aggId.name(), aggregatorId.toString())
                    } else {
                        // Check if the current aggregator is actually parent of requested one
                        if (aggregatorId.parentIdentifier == aggId) {
                            val actorRef = getAggregatorRef(aggregatorId)
                            replyTo ! AggregatorRegistered(requestId, actorRef)
                        } else {
                            // Getting the next aggregator to send the message to
                            val childAggIndex = aggList.indexOf(aggId)+1
                            val childAgg = aggList(childAggIndex)
                            val aggRef = getAggregatorRef(childAgg)
                            aggRef ! trackMsg
                        }
                    }
                }
                this

            case InitiateSampling(samplingPolicy) =>
                context.log.info("Aggregator Id:{} Initiate Sampling", aggId.toString())
                // fetch list of clientIds from the Redis
                val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten

                // TODO create the Job and submit to the python service
                // Make Sampling Job Submit Message here
                val samplingMessage = makeSamplingJobSubmit(clientList)
                context.log.info("Aggregator Id:{} Sampling Message: {}", aggId.toString(), samplingMessage)
                // Convert Message to Json String to send via kafka
                val serializedMsg = JsonEncoder.serialize(samplingMessage)
                // TODO Send job to Python Service using Kafka
                KafkaProducer.send(AGGR_SAMPLING_REQUEST_TOPIC, samplingMessage.__data__.receiverid, serializedMsg)
                
                this

            case StartAggregation(aggregationPolicy) =>
                context.log.info("Aggregator Id:{} Start Aggregation", aggId.toString())

                val aggregationMessage = makeAggregationJobSubmit()
                context.log.info("Aggregator Id:{} Aggregation Message: {}", aggId.toString(), aggregationMessage)

                val serializedMsg = JsonEncoder.serialize(aggregationMessage)
                // TODO Send job to Python Service using Kafka
                KafkaProducer.send(AGGR_AGGREGATION_REQUEST_TOPIC, aggregationMessage.__data__.receiverid, serializedMsg)
                this

            case KafkaResponse(requestId, message) =>
                val msg = JsonDecoder.deserialize(message)
                msg match {
                    case  resp @ JobResponseMessage(_,_) => 
                        resp.__data__.job_type match {
                            case "sampling" =>
                                // TODO: Handle the response appropriately
                                val mp = JsonDecoder.deserialize(resp.__data__.results)
                                mp match {
                                    case l: Map[_,_] =>
                                        val selectedList = l.keySet.toList
                                        parent ! Orchestrator.SamplingCheckpoint(aggId)
                                        // set cycle accepted to 1
                                        selectedList.foreach((c) => RedisClientHelper.hset(c.toString, "cycleAccepted", "1"))
                                        timers.startSingleTimer(TimerKey, CheckS3ForModels(), ConfigManager.aggregatorS3ProbeIntervalMinutes.minutes)
                                    case _ => throw new IllegalArgumentException(s"Invalid response_type : ${resp.__data__.results}")
                                }
                                
                            case "aggregate" => 
                                // TODO: Handle the reponse appropriately
                                AmazonS3Communicator.emptyDir(AmazonS3Communicator.s3Config.getString("bucket"), s"/clients/${aggId.toString()}/")
                                round_index += 1
                                val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
                                clientList.foreach((c) => RedisClientHelper.hset(c, "cycleAccepted", "0"))
                            case _ => throw new IllegalArgumentException(s"Invalid response_type : ${msg}")
                        }
                        
                    case _ => throw new IllegalArgumentException(s"Invalid response_type : ${msg}")
                }
                this

            case trackMsg @ CheckS3ForModels() =>
                // Connect to S3, and ask for models
                context.log.info("Aggregator ID:{} CheckS3ForModels", aggId.toString())
                val modelList = AmazonS3Communicator.listAllFiles(AmazonS3Communicator.s3Config.getString("bucket"), s"/clients/${aggId.toString()}/")

                if (modelList.length >= ConfigManager.minClientsForAggregation) {
                    timers.cancel()
                    context.self ! StartAggregation(ConfigManager.aggregationPolicy)
                } else {
                    timers.startSingleTimer(TimerKey, CheckS3ForModels(), ConfigManager.aggregatorS3ProbeIntervalMinutes.minutes)
                }
                this
            
            case trackMsg @ RequestRealTimeGraph(requestId, entity, replyTo) =>
                entity match {
                    case Left(x) => 
                        context.log.info("Cannot get realTimeGraph for an orchestrator entity: got {}", x.toString())

                    case Right(x) => 
                        if (aggId == x) {
                            // return/build the current node's realTimeGraph
                            context.log.info("Creating new realTimeGraph query actor for {}", entity)
                            context.spawnAnonymous(RealTimeGraphQuery(
                              creator = entity,
                              aggIdToRefMap = aggregatorIdsToRef.toMap,
                              traIds = Some(trainerIdsToRef.keys.toList),
                              requestId = requestId,
                              requester = replyTo,
                              timeout = 30.seconds
                            ))
                        } else {
                            val aggList = x.getAggregators()
                            if (aggList.find(y => {aggId == y}) == None) {
                                context.log.info("Aggregator with id {} not found in {}", aggId.name(), x.toString())
                                this
                            }

                            val childAggIndex = aggList.indexOf(aggId)+1
                            val childAgg = aggList(childAggIndex)
                            val aggRef = getAggregatorRef(childAgg)
                            aggRef ! trackMsg
                        }
                }
                this
            
            case AggregatorTerminated(actor, aggId) =>
                context.log.info("Aggregator with id {} has been terminated", aggId.toString())
                // TODO
                this
            
            case TrainerTerminated(actor, traId) =>
                context.log.info("Trainer with id {} has been terminated", traId.toString())
                // TODO
                this
        }
    
    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("Aggregator {} stopped", aggId.toString())
            this
    }
}

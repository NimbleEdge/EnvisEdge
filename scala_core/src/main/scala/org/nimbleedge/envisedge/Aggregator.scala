package org.nimbleedge.envisedge

import models._
import Types._
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
    def apply(aggId: AggregatorIdentifier, cycleId: CycleId, parent: ActorRef[Orchestrator.Command], routerRef: ActorRef[LocalRouter.Command]): Behavior[Command] =
        Behaviors.setup{context =>
            Behaviors.withTimers { timers =>
                new Aggregator(context, timers, aggId, cycleId, parent, routerRef)
            }
        }
    
    trait Command

    // In case of any Trainer / Aggregator (Child) Termination
    private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
        extends Aggregator.Command
    
    private final case class TrainerTerminated(actor: ActorRef[Trainer.Command], traId: TrainerIdentifier)
        extends Aggregator.Command

    final case class InitiateSampling(samplingPolicy: String, roundIdx: Int, cyId: CycleId) extends Aggregator.Command
    private final case class StartAggregation(aggregationPolicy: String) extends Aggregator.Command

    final case class CheckRedisForModels() extends Aggregator.Command

    private case object TimerKey

    // TODO
    // Add messages here

}
// TODO: parent should be either of orchestrator or aggregator.
class Aggregator(context: ActorContext[Aggregator.Command], timers: TimerScheduler[Aggregator.Command], aggId: AggregatorIdentifier, cycId: CycleId, parent: ActorRef[Orchestrator.Command], routerRef: ActorRef[LocalRouter.Command]) extends AbstractBehavior[Aggregator.Command](context) {
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

    private var roundIndex = 1

    private var cycleId = cycId

    private var curModelVersion = s"${cycleId}_${aggId.toString}_${roundIndex-1}"

    private var aggStateDict: Map[String, Object] = Map(
        "model" -> Message(
            __type__ = "fedrec.data_models.state_tensors_model.StateTensors",
            __data__ = Map("storage" -> s"models/${aggId.getOrchestrator().name()}/${aggId.name()}/${curModelVersion}.pt")
        )
    )

    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), s"models/${aggId.getOrchestrator().name()}/${aggId.name()}/")
    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), s"clients/${aggId.getOrchestrator().name()}/${aggId.name()}/")

    context.log.info("Aggregator {} started", aggId.toString())

    def updateCurModelVersion() = {
        curModelVersion = s"${cycleId}_${aggId.toString}_${roundIndex-1}"
    }

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
                val actorRef = context.spawn(Aggregator(aggregatorId, cycleId, parent, routerRef), s"aggregator-${aggregatorId.name()}")
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

    def getInNeighbours() : Map[String, Message] = {
        val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
        var neighbours: MutableMap[String, Message] = MutableMap.empty
        val versions = RedisClientPoolHelper.hget(clientList, "modelVersion")
        val clients = clientList zip versions
        for((c,v) <- clients) {
            if (v.get == curModelVersion) {
                neighbours += (c -> Message (
                    __type__ = "fedrec.data_models.aggregator_state_model.Neighbour",
                    __data__ = Neighbour (
                        worker_id = c,
                        last_sync = 0,
                        fl_cycle = cycleId.toString,
                        round_idx = roundIndex,
                        storage = s"clients/${aggId.getOrchestrator().name()}/${aggId.name()}/",
                        state_dict = Map (
                            "model" -> Message(
                                __type__ = "fedrec.data_models.state_tensors_model.StateTensors",
                                __data__ = Map(
                                    "storage" -> s"clients/${aggId.getOrchestrator().name()}/${aggId.name()}/${cycleId}_${c}_${roundIndex}.pt"
                                )
                            )
                        ),
                        sample_num = 1
                    )
                ))
            }
        }
        context.log.info(s"Neighbours: ${neighbours}")
        return Map.empty ++ neighbours
    }

    def makeSamplingJobSubmit(clientList: List[String]) : Message = {
        println("In make Sampling message")
        println(trainerIdsToRef)
        return Message (
            __type__ = "fedrec.data_models.job_submit_model.JobSubmitMessage",
            __data__ = JobSubmitMessage (
                job_args = List(clientList),
                job_kwargs = Map(),
                senderid = aggId.toString(),
                receiverid = aggId.toString(),
                job_type = "sample_clients",
                workerstate = Message (
                    __type__ = "fedrec.data_models.aggregator_state_model.AggregatorState",
                    __data__ = AggregatorState (
                        worker_id = aggId.name(),
                        round_idx = roundIndex,
                        fl_cycle = cycleId.toString,
                        state_dict = null,
                        storage = s"models/${aggId.getOrchestrator().name()}/${aggId.name()}/",
                        in_neighbours = Map(),
                        out_neighbours = Map(),
                    )
                )
            )
        )
    }

    def makeAggregationJobSubmit(in_neighbours: Map[String, Message]) : Message = {
        println("In make Aggregation message")
        return Message (
            __type__ = "fedrec.data_models.job_submit_model.JobSubmitMessage",
            __data__ = JobSubmitMessage (
                job_args = List(),
                job_kwargs = Map(),
                senderid = aggId.toString(),
                receiverid = aggId.toString(), // confirm this
                job_type = "aggregate",
                workerstate = Message (
                    __type__ = "fedrec.data_models.aggregator_state_model.AggregatorState",
                    __data__ = AggregatorState (
                        worker_id = aggId.toString(),
                        round_idx = roundIndex,
                        fl_cycle = cycleId.toString,
                        storage = s"models/${aggId.getOrchestrator().name()}/${aggId.name()}/", // Confirm this
                        state_dict = aggStateDict,
                        in_neighbours = in_neighbours,
                        out_neighbours = Map(),
                    )
                )
            )
        )
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

            case InitiateSampling(samplingPolicy, roundIdx, cyId) =>
                context.log.info("Aggregator Id:{} Initiate Sampling", aggId.toString())
                roundIndex = roundIdx
                cycleId = cyId
                updateCurModelVersion()
                // fetch list of clientIds from the Redis
                val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
                context.log.info("Sampling list: {}", clientList)

                // TODO create the Job and submit to the python service
                // Make Sampling Job Submit Message here
                val samplingMessage = makeSamplingJobSubmit(clientList)
                context.log.info("Aggregator Id:{} Sampling Message: {}", aggId.toString(), samplingMessage)
                // Convert Message to Json String to send via kafka
                val serializedMsg = JsonEncoder.serialize(samplingMessage)
                // TODO Send job to Python Service using Kafka
                KafkaProducer.send(AGGR_SAMPLING_REQUEST_TOPIC, aggId.toString(), serializedMsg)
                
                this

            case StartAggregation(aggregationPolicy) =>
                context.log.info("Aggregator Id:{} Start Aggregation", aggId.toString())

                val neighbours = getInNeighbours()
                val aggregationMessage = makeAggregationJobSubmit(neighbours)
                context.log.info("Aggregator Id:{} Aggregation Message: {}", aggId.toString(), aggregationMessage)

                val serializedMsg = JsonEncoder.serialize(aggregationMessage)
                KafkaProducer.send(AGGR_AGGREGATION_REQUEST_TOPIC, aggId.toString(), serializedMsg)
                this

            case KafkaResponse(requestId, message) =>
                val msg = JsonDecoder.deserialize(message)
                msg match {
                    case  resp: JobResponseMessage => 
                        resp.job_type match {
                            case "sample_clients" =>
                                // TODO: Handle the response appropriately
                                val res = resp.results.asInstanceOf[Map[String, List[String]]]
                                var selectedList = res("clients")
                                parent ! Orchestrator.SamplingCheckpoint(aggId)
                                if (ConfigManager.testBuild) {
                                    selectedList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
                                }
                                // set cycle accepted to 1
                                RedisClientPoolHelper.hmset(selectedList, Map("cycleAccepted" -> 1, "roundIdx" -> roundIndex, "cycleIdx" -> cycleId))
                                timers.startSingleTimer(TimerKey, CheckRedisForModels(), ConfigManager.aggregatorS3ProbeIntervalMinutes.minutes)
                                
                            case "aggregate" => 
                                // TODO: Handle the reponse appropriately
                                aggStateDict = resp.results
                                parent ! Orchestrator.AggregationCheckpoint(aggId)
                                val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
                                RedisClientHelper.hset("models", curModelVersion, "1")
                                RedisClientPoolHelper.hset(clientList, "cycleAccepted", "0")
                            case _ => throw new IllegalArgumentException(s"Invalid response_type : ${resp}")
                        }
                        
                    case _ => throw new IllegalArgumentException(s"Invalid response_type : ${msg}")
                }
                this

            case trackMsg @ CheckRedisForModels() =>
                // Connect to S3, and ask for models
                context.log.info("Aggregator ID:{} CheckRedisForModels", aggId.toString())
                var num_models = 0
                
                val clientList = RedisClientHelper.getList(aggId.toString()).toList.flatten.flatten
                val versions = RedisClientPoolHelper.hget(clientList, "modelVersion")
                versions.foreach((v) => {
                    if (v.get == curModelVersion) {
                        num_models += 1
                    }
                })

                if (num_models >= ConfigManager.minClientsForAggregation) {
                    timers.cancel()
                    context.self ! StartAggregation(ConfigManager.aggregationPolicy)
                } else {
                    timers.startSingleTimer(TimerKey, CheckRedisForModels(), ConfigManager.aggregatorS3ProbeIntervalMinutes.minutes)
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

package org.nimbleedge.envisedge

import models._
import scala.collection.mutable.{Map => MutableMap, ListBuffer}

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop
import akka.actor.typed.DispatcherSelector

object FLSystemManager {
    def apply(): Behavior[Command] =
        Behaviors.setup[Command](new FLSystemManager(_))

    sealed trait Command

    // Creating + Getting the actor references
    final case class RequestOrchestrator(requestId: Long, orcId: OrchestratorIdentifier, replyTo: ActorRef[OrchestratorRegistered])
        extends FLSystemManager.Command
    
    final case class OrchestratorRegistered(requestId: Long, actor: ActorRef[Orchestrator.Command])

    final case class RequestAggregator(requestId: Long, aggId: AggregatorIdentifier, replyTo: ActorRef[AggregatorRegistered])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    final case class AggregatorRegistered(requestId: Long, actor: ActorRef[Aggregator.Command])

    final case class RegisterDevice(deviceId: String) extends FLSystemManager.Command
    final case class DeviceRegistered(clientId: String)

    final case class RequestTrainer(requestId: Long, traId: TrainerIdentifier, replyTo: ActorRef[TrainerRegistered])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    final case class TrainerRegistered(requestId: Long, actor: ActorRef[Trainer.Command])
    
    // In case of an Orchestrator Termination
    private final case class OrchestratorTerminated(actor: ActorRef[Orchestrator.Command], orcId: OrchestratorIdentifier)
        extends FLSystemManager.Command

    // Requesting RealTimeGraph
    final case class RequestRealTimeGraph(requestId: Long, entity: Either[OrchestratorIdentifier, AggregatorIdentifier], replyTo: ActorRef[RespondRealTimeGraph])
        extends FLSystemManager.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    final case class RespondRealTimeGraph(requestId: Long, realTimeGraph: TopologyTree)

    final case class KafkaResponse(receiverId: String, message: String) extends Command with LocalRouter.Command with Aggregator.Command

    // Start cycle
    // TODO
    // final case class StartCycle(requestId: Long, replyTo: ActorRef[RespondModel]) extends FLSystemManager.Command with Orchestrator.Command with Aggregator.Command
    final case class StartCycle(taskId : String) extends FLSystemManager.Command with Orchestrator.Command
    final case class SamplingCheckpoint(orcId : OrchestratorIdentifier) extends FLSystemManager.Command
    final case class AggregationCheckpoint(orcId : OrchestratorIdentifier, roundIdx: Int) extends FLSystemManager.Command
    final case class RespondModel(requestId: Long)

    // TODO
    // Add more messages
}

class FLSystemManager(context: ActorContext[FLSystemManager.Command]) extends AbstractBehavior[FLSystemManager.Command](context) {
    import FLSystemManager._

    // TODO
    // Topology ??
    // State Information
    var orcIdToRef : MutableMap[OrchestratorIdentifier, ActorRef[Orchestrator.Command]] = MutableMap.empty

    // Will use this taskList to spawn Orchestrator
    var taskList : ListBuffer[String] = ListBuffer.empty

    // TODO insert host, port from config
    RedisClientHelper.initConnection()

    context.log.info("FLSystemManager Started")

    KafkaProducer.init(ConfigManager.staticConfig.getConfig("producer-config"))

    val FLSysKafkaConsumerRef = context.spawn(
        KafkaConsumer(ConfigManager.staticConfig.getConfig("consumer-config"), Right(context.self)), "FLSystemManagerKafkaConsumer", DispatcherSelector.blocking()
    )

    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), "models/")
    AmazonS3Communicator.createEmptyDir(AmazonS3Communicator.s3Config.getString("bucket"), "clients/")

    private def getOrchestratorRef(orcId: OrchestratorIdentifier): ActorRef[Orchestrator.Command] = {
        orcIdToRef.get(orcId) match {
            case Some(actorRef) =>
                actorRef
            case None =>
                context.log.info("Creating new orchestrator actor for {}", orcId.name())
                val actorRef = context.spawn(Orchestrator(orcId, context.self), s"orchestrator-${orcId.name()}")
                context.watchWith(actorRef, OrchestratorTerminated(actorRef, orcId))
                orcIdToRef += orcId -> actorRef
                actorRef
        }
    }

    override def onMessage(msg: Command): Behavior[Command] =
        msg match {
            case RequestOrchestrator(requestId, orcId, replyTo) =>
                val actorRef = getOrchestratorRef(orcId)
                replyTo ! OrchestratorRegistered(requestId, actorRef)
                this
            
            case trackMsg @ RequestAggregator(requestId, aggId, replyTo) =>
                val orcId = aggId.getOrchestrator()

                val orchestratorRef = getOrchestratorRef(orcId)
                orchestratorRef ! trackMsg
                this
            
            case trackMsg @ RequestTrainer(requestId, traId, replyTo) =>
                val orcId = traId.getOrchestrator()

                val orchestratorRef = getOrchestratorRef(orcId)
                orchestratorRef ! trackMsg
                this
            
            case trackMsg @ RequestRealTimeGraph(requestId, entity, replyTo) =>
                val orcId = entity match {
                    case Left(x) => x
                    case Right(x) => x.getOrchestrator()
                }

                orcIdToRef.get(orcId) match {
                    case Some(actorRef) =>
                        actorRef ! trackMsg
                    case None =>
                        context.log.info("Orchestrator with id {} does not exist, can't request realTimeGraph", orcId.name())
                }
                this

            case RegisterDevice(deviceId) =>
                //TODO
                var taskId : String = ConfigManager.DEFAULT_TASK_ID
                if (!taskList.isEmpty) {
                    taskId = taskList.head
                } else {
                    taskList += taskId
                }

                val orcId = ConfigManager.getOrcId(taskId)
                val orcRef = getOrchestratorRef(orcId)
                orcRef ! Orchestrator.RegisterDevice(deviceId)
                this
            
            case startCycle @ StartCycle(taskId) =>
                context.log.info("Start Cycle Message Received -> FL System Manager")
                // TODO what to do if no orchestrator
                val orcRef = getOrchestratorRef(OrchestratorIdentifier(taskId))
                orcRef ! startCycle
                this

            case SamplingCheckpoint(orcId) =>
                context.log.info("FLSystemManager: Samping finished for OrcID:{}", orcId.name())
                // inform HTTP Service to broadcast start cycle
                KafkaProducer.send(ConfigManager.FLSYS_REQUEST_TOPIC, "StartCycle", orcId.name())
                this
            
            case OrchestratorTerminated(actor, orcId) =>
                context.log.info("Orchestrator with id {} has been terminated", orcId.name())
                // TODO cycle termination
                this

            case AggregationCheckpoint(orcId, roundIdx) =>
                context.log.info("FLSystemManager: Aggregation finished")
                // inform HTTP Service to broadcast update model 
                KafkaProducer.send(ConfigManager.FLSYS_REQUEST_TOPIC, "CycleTerminated", orcId.name())
                if (roundIdx == ConfigManager.NUM_ROUNDS) {
                    getOrchestratorRef(orcId) ! Orchestrator.ResetRoundIdx()
                }
                this

            case KafkaResponse(requestId, message) => 
                //val msg = JsonDecoder.deserialize(message)
                requestId match {
                    case "Register" =>
                        context.self ! RegisterDevice(message)
                        this
                    case "StartCycle" =>
                        context.self ! StartCycle(message)
                        this
                }
        }

    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("FLSystemManager Stopped")
            this
    }
}
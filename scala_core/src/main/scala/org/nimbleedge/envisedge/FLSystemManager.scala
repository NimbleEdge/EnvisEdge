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

    final case class RegisterDevice(deviceId: String, replyTo: ActorRef[DeviceRegistered]) extends FLSystemManager.Command
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

    // Start cycle
    // TODO
    // final case class StartCycle(requestId: Long, replyTo: ActorRef[RespondModel]) extends FLSystemManager.Command with Orchestrator.Command with Aggregator.Command
    final case class StartCycle(requestId : Long) extends FLSystemManager.Command with Orchestrator.Command with Aggregator.Command
    final case class SamplingCheckpoint(orcId : OrchestratorIdentifier) extends FLSystemManager.Command
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

            case RegisterDevice(deviceId, replyTo) =>
                var taskId : String = ConfigManager.DEFAULT_TASK_ID
                if (!taskList.isEmpty) {
                    taskId = taskList.head
                }

                val orcId = ConfigManager.getOrcId(taskId)
                val orcRef = getOrchestratorRef(orcId)
                orcRef ! Orchestrator.RegisterDevice(deviceId, replyTo)
                this
            
            case startCycle @ StartCycle(_) =>
                context.log.info("Start Cycle Message Received -> FL System Manager")
                // TODO what to do if no orchestrator
                orcIdToRef.values.foreach((o) => o ! startCycle)
                this

            case SamplingCheckpoint(orcId) =>
                context.log.info("FLSystemManager: Samping finished for OrcID:{}", orcId.name())
                // TODO inform HTTP Service to broadcast start cycle
                this
            
            case OrchestratorTerminated(actor, orcId) =>
                context.log.info("Orchestrator with id {} has been terminated", orcId.name())
                // TODO
                this
        }

    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("FLSystemManager Stopped")
            this
    }
}
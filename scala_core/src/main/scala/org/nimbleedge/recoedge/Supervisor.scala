package org.nimbleedge.recoedge

import models._
import scala.collection.mutable.{Map => MutableMap}

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop

object Supervisor {
    def apply(): Behavior[Command] =
        Behaviors.setup[Command](new Supervisor(_))

    sealed trait Command

    // Creating + Getting the actor references
    final case class RequestOrchestrator(requestId: Long, orcId: OrchestratorIdentifier, replyTo: ActorRef[OrchestratorRegistered])
        extends Supervisor.Command
    
    final case class OrchestratorRegistered(requestId: Long, actor: ActorRef[Orchestrator.Command])

    final case class RequestAggregator(requestId: Long, aggId: AggregatorIdentifier, replyTo: ActorRef[AggregatorRegistered])
        extends Supervisor.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    final case class AggregatorRegistered(requestId: Long, actor: ActorRef[Aggregator.Command])

    final case class RequestTrainer(requestId: Long, traId: TrainerIdentifier, replyTo: ActorRef[TrainerRegistered])
        extends Supervisor.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    final case class TrainerRegistered(requestId: Long, actor: ActorRef[Trainer.Command])
    
    // In case of an Orchestrator Termination
    private final case class OrchestratorTerminated(actor: ActorRef[Orchestrator.Command], orcId: OrchestratorIdentifier)
        extends Supervisor.Command

    // Requesting Topology
    final case class RequestTopology(requestId: Long, entity: Either[OrchestratorIdentifier, AggregatorIdentifier], replyTo: ActorRef[Topology])
        extends Supervisor.Command
        with Orchestrator.Command
        with Aggregator.Command
    
    // TODO
    final case class Topology(requestId: Long)

    // Start cycle
    // TODO
    final case class StartCycle(requestId: Long, replyTo: ActorRef[RespondModel]) extends Supervisor.Command
    final case class RespondModel(requestId: Long)

    // TODO
    // Add more messages
}

class Supervisor(context: ActorContext[Supervisor.Command]) extends AbstractBehavior[Supervisor.Command](context) {
    import Supervisor._

    // TODO
    // Topology
    // State Information
    var orcIdToRef : MutableMap[OrchestratorIdentifier, ActorRef[Orchestrator.Command]] = MutableMap.empty

    context.log.info("Supervisor Started")

    private def getOrchestratorRef(orcId: OrchestratorIdentifier): ActorRef[Orchestrator.Command] = {
        orcIdToRef.get(orcId) match {
            case Some(actorRef) =>
                actorRef
            case None =>
                context.log.info("Creating new orchestrator actor for {}", orcId.toString())
                val actorRef = context.spawn(Orchestrator(orcId), s"orchestrator-${orcId.toString()}")
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
            
            case trackMsg @ RequestTopology(requestId, entity, replyTo) =>
                val orcId = entity match {
                    case Left(x) => x
                    case Right(x) => x.getOrchestrator()
                }

                orcIdToRef.get(orcId) match {
                    case Some(actorRef) =>
                        actorRef ! trackMsg
                    case None =>
                        context.log.info("Orchestrator with id {} does not exist, can't request topology", orcId.toString())
                }
                this
            
            case StartCycle(requestId, replyTo) =>
                // TODO
                this
            
            case OrchestratorTerminated(actor, orcId) =>
                context.log.info("Orchestrator with id {} has been terminated", orcId.toString())
                // TODO
                this
        }

    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("Supervisor Stopped")
            this
    }
}
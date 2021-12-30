package org.nimbleedge.recoedge

import models._

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop
import scala.collection.mutable.Map

object Orchestrator {
  def apply(orcId: OrchestratorIdentifier): Behavior[Command] =
    Behaviors.setup(new Orchestrator(_, orcId))

  trait Command

  // In case any Aggregator Termination
  private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
    extends Orchestrator.Command

  // TODO
  // Add messages here
}

class Orchestrator(context: ActorContext[Orchestrator.Command], orcId: OrchestratorIdentifier) extends AbstractBehavior[Orchestrator.Command](context) {
  import Orchestrator._
  import Supervisor.{ RequestAggregator, RequestTrainer, RequestTopology }

  // TODO
  // Add state and persistent information
  var aggIdToRef : Map[AggregatorIdentifier, ActorRef[Aggregator.Command]] = Map.empty
  context.log.info("Orchestrator {} started", orcId.toString())
  
  private def getAggregatorRef(aggId: AggregatorIdentifier): ActorRef[Aggregator.Command] = {
    aggIdToRef.get(aggId) match {
        case Some(actorRef) =>
            actorRef
        case None =>
            context.log.info("Creating new aggregator actor for {}", aggId.toString())
            val actorRef = context.spawn(Aggregator(aggId), s"aggregator-${aggId.toString()}")
            context.watchWith(actorRef, AggregatorTerminated(actorRef, aggId))
            aggIdToRef += aggId -> actorRef
            actorRef
    }
  }

  override def onMessage(msg: Command): Behavior[Command] =
    msg match {
      case trackMsg @ RequestAggregator(requestId, aggId, replyTo) =>
        actorRef = getAggregatorRef(aggId)
        replyTo ! AggregatorRegistered(actorRef)
        this

      case trackMsg @ RequestTrainer(requestId, traId, replyTo) =>
        val traId = traId.toList()[1]

        aggRef = getAggregatorRef(aggId)
        aggRef ! trackMsg
        this
      
      case trackMsg @ RequestTopology(requestId, entity, replyTo) =>
        // TODO
        val aggId = entity.toList()[0]

        orcIdToRef.get(aggId) match {
            case Some(actorRef) =>
                actorRef ! trackMsg
            case None =>
                context.log.info("Orchestrator with id {} does not exist, can't request topology", aggId.toString())
        }
        this
      
      case AggregatorTerminated(actor, aggId) =>
        context.log.info("Aggregator with id {} has been terminated", aggId.toString())
        // TODO
        this
    }
  
  override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
    case PostStop =>
      context.log.info("Orchestrator {} stopeed", orcId.toString())
      this
  }
}
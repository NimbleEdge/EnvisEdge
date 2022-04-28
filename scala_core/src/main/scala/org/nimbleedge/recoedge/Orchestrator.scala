package org.nimbleedge.envisedge


import models._
import scala.concurrent.duration._
import scala.collection.mutable.{Map => MutableMap}

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop

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
  import FLSystemManager.{ RequestAggregator, AggregatorRegistered, RequestTrainer, RequestRealTimeGraph }

  // TODO
  // Add state and persistent information
  var aggIdToRef : MutableMap[AggregatorIdentifier, ActorRef[Aggregator.Command]] = MutableMap.empty
  context.log.info("Orchestrator {} started", orcId.name())
  
  private def getAggregatorRef(aggId: AggregatorIdentifier): ActorRef[Aggregator.Command] = {
    aggIdToRef.get(aggId) match {
        case Some(actorRef) =>
            actorRef
        case None =>
            context.log.info("Creating new aggregator actor for {}", aggId.name())
            val actorRef = context.spawn(Aggregator(aggId), s"aggregator-${aggId.name()}")
            context.watchWith(actorRef, AggregatorTerminated(actorRef, aggId))
            aggIdToRef += aggId -> actorRef
            actorRef
    }
  }

  override def onMessage(msg: Command): Behavior[Command] =
    msg match {
      case trackMsg @ RequestAggregator(requestId, aggId, replyTo) =>
        if (aggId.getOrchestrator() != orcId) {
          context.log.info("Expected orchestrator id {}, found {}", orcId.name(), aggId.toString())
        } else {
          val actorRef = getAggregatorRef(aggId)
          replyTo ! AggregatorRegistered(requestId, actorRef)
        }
        this

      case trackMsg @ RequestTrainer(requestId, traId, replyTo) =>
        if (traId.getOrchestrator() != orcId) {
          context.log.info("Expected orchestrator id {}, found {}", orcId.name(), traId.toString())
        } else {
          val aggList = traId.getAggregators()
          val aggId = aggList.head
          val aggRef = getAggregatorRef(aggId)
          aggRef ! trackMsg
        }
        this
      
      case trackMsg @ RequestRealTimeGraph(requestId, entity, replyTo) =>
        val entityOrcId = entity match {
          case Left(x) => x
          case Right(x) => x.getOrchestrator()
        }

        if (entityOrcId != orcId) {
          context.log.info("Expected orchestrator id {}, found {}", orcId.name(), entityOrcId.name())
        } else {
          entity match {
            case Left(x) =>
              // Give current node's realTimeGraph
              context.log.info("Creating new realTimeGraph query actor for {}", entity)
              context.spawnAnonymous(RealTimeGraphQuery(
                creator = entity,
                aggIdToRefMap = aggIdToRef.toMap,
                traIds = None,
                requestId = requestId,
                requester = replyTo,
                timeout = 30.seconds
              ))
            case Right(x) =>
              // Will always include current aggregator at the head
              val aggList = x.getAggregators()
              val aggId = aggList.head
              val aggRef = getAggregatorRef(aggId)
              aggRef ! trackMsg
          }
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
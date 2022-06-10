package org.nimbleedge.envisedge

import models._
import scala.concurrent.duration._
import scala.collection.mutable.{Map => MutableMap}

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.DispatcherSelector
import akka.actor.typed.Signal
import akka.actor.typed.PostStop

import messages._
import scala.collection.mutable

object Orchestrator {
  def apply(orcId: OrchestratorIdentifier, parent: ActorRef[FLSystemManager.Command]): Behavior[Command] =
    Behaviors.setup(new Orchestrator(_, orcId, parent))

  trait Command

  // In case any Aggregator Termination
  private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
    extends Orchestrator.Command

  final case class RegisterDevice(device: String) extends Orchestrator.Command

  final case class SamplingCheckpoint(aggId: AggregatorIdentifier) extends Orchestrator.Command
  final case class AggregationCheckpoint(aggId: AggregatorIdentifier) extends Orchestrator.Command

  // TODO
  // Add messages here
}

class Orchestrator(context: ActorContext[Orchestrator.Command], orcId: OrchestratorIdentifier, parent: ActorRef[FLSystemManager.Command]) extends AbstractBehavior[Orchestrator.Command](context) {
  import Orchestrator._
  import FLSystemManager.{ RequestAggregator, AggregatorRegistered, RequestTrainer, RequestRealTimeGraph, StartCycle}
  import LocalRouter.RemoveAggregator

  // TODO
  // Add state and persistent information
  var aggIdToRef : MutableMap[AggregatorIdentifier, ActorRef[Aggregator.Command]] = MutableMap.empty
  var aggIdToClientCount : MutableMap[AggregatorIdentifier, Int] = MutableMap.empty

  var aggIdSamplingCompletedSet : mutable.Set[AggregatorIdentifier] = mutable.Set.empty
  var aggIdAggregationCompletedSet : mutable.Set[AggregatorIdentifier] = mutable.Set.empty

  val routerRef = context.spawn(LocalRouter(), s"LocalRouter-${orcId.toString()}")

  val aggKafkaConsumerRef = context.spawn(
      KafkaConsumer(ConfigManager.staticConfig.getConfig("consumer-config"), Left(routerRef)), s"AggregatorKafkaConsumer-${orcId.toString()}", DispatcherSelector.blocking()
  )

  context.log.info("Orchestrator {} started", orcId.name())

  private def spawnAggregator(aggId : AggregatorIdentifier) : ActorRef[Aggregator.Command] = {
    context.log.info("Creating new aggregator actor for {}", aggId.name())
    val actorRef = context.spawn(Aggregator(aggId, context.self, routerRef), s"aggregator-${aggId.name()}")
    context.watchWith(actorRef, AggregatorTerminated(actorRef, aggId))
    aggIdToRef += aggId -> actorRef
    aggIdToClientCount += aggId -> 0

    return actorRef
  }
  
  private def getAggregatorRef(aggId: AggregatorIdentifier): ActorRef[Aggregator.Command] = {
    aggIdToRef.get(aggId) match {
        case Some(actorRef) =>
            actorRef
        case None =>
            val actorRef = spawnAggregator(aggId)
            return actorRef
    }
  }

  private def createAggregator() : AggregatorIdentifier = {
    val aggCount = aggIdToRef.size
    val aggIdStr = "A" + (aggCount + 1)
    val aggId = AggregatorIdentifier(orcId, aggIdStr)

    val actorRef = spawnAggregator(aggId)

    return  aggId
  }

  private def getAvailableAggregator() : AggregatorIdentifier = {
    val filteredMap = aggIdToClientCount.filter(mapEntry => mapEntry._2 < ConfigManager.maxClientsInAgg)
    if (filteredMap.isEmpty) {
      //create new agg
      return createAggregator();
    } else {
      return filteredMap.head._1
    }
  }

  private def reset() = {
    aggIdToClientCount.foreach(agg => aggIdToClientCount.update(agg._1, 0))
    aggIdSamplingCompletedSet  = mutable.Set.empty
    aggIdAggregationCompletedSet  = mutable.Set.empty
  }

  override def onMessage(msg: Command): Behavior[Command] =
    msg match {
      case trackMsg @ RequestAggregator(requestId, aggId, replyTo) =>
        if (aggId.getOrchestrator() != orcId) {
          context.log.info("Expected orchestrator id {}, found {}", orcId.name(), aggId.name())
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

      case RegisterDevice(clientId) =>
        context.log.info("Orc id:{} device registration for device:{}", orcId.name(), device)
        val clientId = "client-" + device
        val aggId = getAvailableAggregator()
        //update this pair to the redis
        val dataMap = Map("clientId" -> clientId, "aggId" -> aggId.toString(), "orcId" -> orcId.name(), "cycleAccepted" -> 0)
        RedisClientHelper.hmset(device, dataMap)
        RedisClientHelper.rpush(aggId.toString(), clientId)

        aggIdToClientCount(aggId) += 1
        this

      
      case AggregatorTerminated(actor, aggId) =>
        context.log.info("Aggregator with id {} has been terminated", aggId.toString())
        routerRef ! RemoveAggregator(aggId.toString())
        // TODO
        this

      case StartCycle(_) =>
        val aggMsg = Aggregator.InitiateSampling(ConfigManager.samplingPolicy)
        aggIdToRef.values.foreach((a) => a ! aggMsg)
        this

      case SamplingCheckpoint(aggId) =>
        context.log.info("Orc id:{} Sampling Checkpoint for Agg:{}", orcId.name(), aggId.name())
        aggIdSamplingCompletedSet += aggId
        if (aggIdSamplingCompletedSet.size == orcId.getChildren().size) {
          context.log.info("Orc id:{} Sampling Checkpoint Finished for all Aggs, sending next checkpoint to FLSystemManager", orcId.name())
          parent ! FLSystemManager.SamplingCheckpoint(orcId)
        }
        this

      case AggregationCheckpoint(aggId) =>
        context.log.info("Orc id:{} Aggregation Checkpoint for Agg:{}", orcId.name(), aggId.name())
        aggIdAggregationCompletedSet += aggId
        if (aggIdAggregationCompletedSet.size == orcId.getChildren().size) {
          context.log.info("Orc id:{} Aggregation Checkpoint Finished for all Aggs, sending next checkpoint to FLSystemManager", orcId.name())
          parent ! FLSystemManager.AggregationCheckpoint(orcId)
        }
        // reset all sturctures
        reset()
        this

    }
  
  override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
    case PostStop =>
      context.log.info("Orchestrator {} stopped", orcId.name())
      this
  }
}

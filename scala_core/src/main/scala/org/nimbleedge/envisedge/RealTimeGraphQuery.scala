package org.nimbleedge.envisedge

import org.nimbleedge.envisedge.models._
import scala.concurrent.duration.FiniteDuration
import akka.actor.typed.Behavior
import akka.actor.typed.ActorRef
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.TimerScheduler
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.PostStop
import akka.actor.typed.Signal

import FLSystemManager.{RespondRealTimeGraph}

// Map of Aggregator Identifiers is compulsory
// List of Trainer Identifiers is optional

object RealTimeGraphQuery {
  def apply(
      creator: Either[OrchestratorIdentifier, AggregatorIdentifier],
      aggIdToRefMap: Map[AggregatorIdentifier, ActorRef[Aggregator.Command]],
      traIds: Option[List[TrainerIdentifier]],
      requestId: Long,
      requester: ActorRef[RespondRealTimeGraph],
      timeout: FiniteDuration
  ): Behavior[Command] = {
    Behaviors.setup { context =>
      Behaviors.withTimers { timers =>
        new RealTimeGraphQuery(
          creator,
          aggIdToRefMap,
          traIds,
          requestId,
          requester,
          timeout,
          context,
          timers
        )
      }
    }
  }

  trait Command
  private case object CollectionTimeout extends Command

  final case class WrappedRespondRealTimeGraph(response: RespondRealTimeGraph) extends Command

  private final case class AggregatorTerminated(aggId: AggregatorIdentifier) extends Command
}

class RealTimeGraphQuery(
    creator: Either[OrchestratorIdentifier, AggregatorIdentifier],
    aggIdToRefMap: Map[AggregatorIdentifier, ActorRef[Aggregator.Command]],
    traIds: Option[List[TrainerIdentifier]],
    requestId: Long,
    requester: ActorRef[RespondRealTimeGraph],
    timeout: FiniteDuration,
    context: ActorContext[RealTimeGraphQuery.Command],
    timers: TimerScheduler[RealTimeGraphQuery.Command]
) extends AbstractBehavior[RealTimeGraphQuery.Command](context) {
  import RealTimeGraphQuery._

  timers.startSingleTimer(CollectionTimeout, CollectionTimeout, timeout)

  private val respondRealTimeGraphAdapter =
    context.messageAdapter(WrappedRespondRealTimeGraph.apply)

  private var repliesSoFar = Map.empty[AggregatorIdentifier, TopologyTree]
  private var stillWaiting = aggIdToRefMap.keySet

  context.log.info("RealTimeGraphQuery Actor for {} started", creator)

  if (aggIdToRefMap.isEmpty) {
    respondWhenAllCollected()
  } else {
    aggIdToRefMap.foreach { case (aggId, aggRef) =>
      context.watchWith(aggRef, AggregatorTerminated(aggId))
      aggRef ! FLSystemManager.RequestRealTimeGraph(
        0,
        Right(aggId),
        respondRealTimeGraphAdapter
      )
    }
  }

  override def onMessage(msg: Command): Behavior[Command] =
    msg match {
      case WrappedRespondRealTimeGraph(response) =>
        onRespondRealTimeGraph(response)
      case AggregatorTerminated(aggId) => onAggregatorTerminated(aggId)
      case CollectionTimeout           => onCollectionTimeout()
    }

  private def onRespondRealTimeGraph(
      response: RespondRealTimeGraph
  ): Behavior[Command] = {
    val realTimeGraph = response.realTimeGraph
    val aggId: AggregatorIdentifier = response.realTimeGraph match {

      // The Topology Tree will always be a node since
      // We are requesting realTimeGraph only from Orchestrator/Aggregators.

      case Leaf(x) => throw new NotImplementedError
      case Node(value, children) =>
        value match {

          // OrchestratorIdentifier is never used!
          // The entity received here should not be Orchestrator Identifier
          // Since these are messages which will be received by self.

          case Left(x)  => throw new NotImplementedError
          case Right(x) => x
        }
    }

    repliesSoFar += (aggId -> realTimeGraph)
    stillWaiting -= aggId
    respondWhenAllCollected()
  }

  private def onAggregatorTerminated(
      aggId: AggregatorIdentifier
  ): Behavior[Command] = {
    if (stillWaiting(aggId)) {
      // Send the empty List of children when Aggregator terminated.
      repliesSoFar += (aggId -> Node(Right(aggId), Set.empty))
      stillWaiting -= aggId
    }
    respondWhenAllCollected()
  }

  private def onCollectionTimeout(): Behavior[Command] = {
    // Send the empty List of children for Aggregators who didn't respond
    repliesSoFar ++= stillWaiting.map(aggId => aggId -> Node(Right(aggId), Set.empty))
    stillWaiting = Set.empty
    respondWhenAllCollected()
  }

  private def respondWhenAllCollected(): Behavior[Command] = {
    if (stillWaiting.isEmpty) {
      // Construct a tree and return to requester
      val children: Set[TopologyTree] = {
        val trainers: Set[TopologyTree] = traIds match {
          case Some(list) => list.map(traId => Leaf(traId)).toSet
          case None       => Set.empty
        }
        repliesSoFar.values.toSet ++ trainers
      }
      requester ! RespondRealTimeGraph(requestId, Node(creator, children))
      Behaviors.stopped
    } else {
      this
    }
  }

  override def onSignal: PartialFunction[Signal, Behavior[Command]] = { case PostStop =>
    context.log.info("RealTimeGraphQuery Actor for {} stopped", creator)
    this
  }
}

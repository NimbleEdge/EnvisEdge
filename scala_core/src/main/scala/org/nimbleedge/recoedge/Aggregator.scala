package org.nimbleedge.recoedge

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

object Aggregator {
    def apply(aggId: AggregatorIdentifier): Behavior[Command] =
        Behaviors.setup(new Aggregator(_, aggId))
    
    trait Command

    // In case of any Trainer / Aggregator (Child) Termination
    private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
        extends Aggregator.Command
    
    private final case class TrainerTerminated(actor: ActorRef[Trainer.Command], traId: TrainerIdentifier)
        extends Aggregator.Command

    // TODO
    // Add messages here
}

class Aggregator(context: ActorContext[Aggregator.Command], aggId: AggregatorIdentifier) extends AbstractBehavior[Aggregator.Command](context) {
    import Aggregator._
    import FLSystemManager.{ RequestTrainer, TrainerRegistered, RequestAggregator, AggregatorRegistered, RequestRealTimeGraph }

    // TODO
    // Add state and persistent information

    // List of Aggregators which are children of this aggregator
    var aggregatorIdsToRef : MutableMap[AggregatorIdentifier, ActorRef[Aggregator.Command]] = MutableMap.empty

    // List of trainers which are children of this aggregator
    var trainerIdsToRef : MutableMap[TrainerIdentifier, ActorRef[Trainer.Command]] = MutableMap.empty

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
                val actorRef = context.spawn(Aggregator(aggregatorId), s"aggregator-${aggregatorId.name()}")
                context.watchWith(actorRef, AggregatorTerminated(actorRef, aggregatorId))
                aggregatorIdsToRef += aggregatorId -> actorRef
                actorRef
        }
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
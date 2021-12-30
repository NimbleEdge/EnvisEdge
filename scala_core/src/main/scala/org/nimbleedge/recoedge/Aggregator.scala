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

object Aggregator {
    def apply(aggId: AggregatorIdentifier): Behavior[Command] =
        Behaviors.setup(new Aggregator(_, aggId))
    
    trait Command

    // In cae of any Trainer / Aggregator (Chile) Termination
    private final case class AggregatorTerminated(actor: ActorRef[Aggregator.Command], aggId: AggregatorIdentifier)
        extends Aggregator.Command
    
    private final case class TrainerTerminated(actor: ActorRef[Trainer.Command], traId: TrainerIdentifier)
        extends Aggregator.Command

    // TODO
    // Add messages here
}

class Aggregator(context: ActorContext[Aggregator.Command], aggId: AggregatorIdentifier) extends AbstractBehavior[Aggregator.Command](context) {
    import Aggregator._
    import Supervisor.{ RequestTrainer, RequestTopology }

    // TODO
    // Add state and persistent information
    var aggregatorIdsToRef : Map[AggregatorIdentifier, ActorRef[Aggregator.Command]] = Map.empty
    var trainerIdsToRef : Map[TrainerIdentifier, ActorRef[Trainer.Command]] = Map.empty

    context.log.info("Aggregator {} started", aggId.toString())

    override def onMessage(msg: Command): Behavior[Command] =

        msg match {
            case trackMsg @ RequestTrainer(requestId, trainerId , replyTo) =>
                trainerIdsToRef.get(trainerId) match {
                    case Some(actorRef) =>
                        // Need to check whether the trainer parent is valid or not using aggId 
                        replyTo ! TrainerIdentifier(actorRef)    
                    case None =>
                        context.log.info("Creating new Trainer actor for {}", trackMsg.trainerId.toString())
                        val actorRef = context.spawn(Trainer(trainerId), s"trainer-${trackMsg.trainerId.toString()}")
                        context.watchWith(actorRef, TrainerTerminated(actorRef, trainerId))
                        trainerIdsToRef += trainerId -> actorRef
                        replyTo ! TrainerRegistered(actorRef)
                }
                this

            case trackMsg @ RequestAggregator(requestId, aggregatorId , replyTo) =>
                aggregatorIdsToRef.get(aggregatorId) match {
                    case Some(actorRef) =>
                        replyTo ! AggregatorIdentifier(actorRef)    
                    case None =>
                        context.log.info("Creating new Aggregator actor for {}", trackMsg.aggregatorId.toString())
                        val actorRef = context.spawn(Aggregator(aggregatorId), s"aggregator-${trackMsg.aggregatorId.toString()}")
                        context.watchWith(actorRef, AggregatorTerminated(actorRef, trainerId))
                        aggregatorIdsToRef += aggregatorId -> actorRef
                        replyTo ! AggregatorRegistered(actorRef)
                }
                this    
            
            case trackMsg @ RequestTopology(requestId, entity, replyTo) =>
                // TODO
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
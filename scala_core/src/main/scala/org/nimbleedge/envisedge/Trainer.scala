package org.nimbleedge.envisedge

import models._

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.DispatcherSelector
import akka.actor.typed.PostStop

object Trainer {
    def apply(traId: TrainerIdentifier): Behavior[Command] =
        Behaviors.setup(new Trainer(_, traId))
    
    trait Command

    final case class JobResponse(response: String) extends Command
    final case class HelperTerminated(actorRef: ActorRef[TrainerHelper.Command]) extends Command

    // TODO
    // Add messages here
}

class Trainer(context: ActorContext[Trainer.Command], traId: TrainerIdentifier) extends AbstractBehavior[Trainer.Command](context) {
    import Trainer._
    import TrainerHelper.{Send,Receive}
    import Orchestrator.JobSubmit

    // TODO
    // Add state and persistent information

    context.log.info("Trainer {} started", traId.toString())

    private final val topic = "Trainer-" + traId.name()

    override def onMessage(msg: Command): Behavior[Command] =
        msg match {
            case JobSubmit(job) => 
                val actorRef = context.spawn(TrainerHelper(traId),s"trainer-helper-${traId.name()}",DispatcherSelector.blocking())
                context.watchWith(actorRef, HelperTerminated(actorRef))
                actorRef ! Send(topic, job)
                actorRef ! Receive(topic, context.self)
                this

            // TODO
            case JobResponse(message) => 
                if (message == "Timeout") {
                    context.log.info("Trainer Helper {} timeout.", traId.name())
                }
                this

            case HelperTerminated(_) => 
                context.log.info("Trainer {} Helper has been terminated", traId.name())
                this
        }
    
    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("Trainer {} stopped", traId.toString())
            this
    }
}
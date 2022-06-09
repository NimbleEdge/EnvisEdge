package org.nimbleedge.envisedge

import models._

import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop

object Trainer {
  def apply(traId: TrainerIdentifier): Behavior[Command] =
    Behaviors.setup(new Trainer(_, traId))

  trait Command

  // TODO
  // Add messages here
}

class Trainer(context: ActorContext[Trainer.Command], traId: TrainerIdentifier)
    extends AbstractBehavior[Trainer.Command](context) {
  import Trainer._

  // TODO
  // Add state and persistent information

  context.log.info("Trainer {} started", traId.toString())

  override def onMessage(msg: Command): Behavior[Command] =
    msg match {
      // TODO
      case _ =>
        this
    }

  override def onSignal: PartialFunction[Signal, Behavior[Command]] = { case PostStop =>
    context.log.info("Trainer {} stopped", traId.toString())
    this
  }
}

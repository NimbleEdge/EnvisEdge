package org.nimbleedge.envisedge

import akka.actor.typed.Behavior
import akka.actor.typed.Signal
import akka.actor.typed.PostStop
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.Behaviors

object SimulatorSupervisor {
	// Update this to manager to other entities
	def apply(): Behavior[Nothing] =
		Behaviors.setup[Nothing](new SimulatorSupervisor(_))
}

class SimulatorSupervisor(context: ActorContext[Nothing]) extends AbstractBehavior[Nothing](context) {
	context.log.info("Simulator Supervisor started")

	override def onMessage(msg: Nothing): Behavior[Nothing] = {
		Behaviors.unhandled
	}

	override def onSignal: PartialFunction[Signal, Behavior[Nothing]] = {
		case PostStop =>
			context.log.info("Simulator Supervisor stopped")
			this
	}
}
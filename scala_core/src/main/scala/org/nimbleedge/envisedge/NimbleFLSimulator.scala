package org.nimbleedge.envisedge

import akka.actor.typed.ActorSystem

object NimbleFLSimulator {
	def main(args: Array[String]): Unit = {
		for (arg<-args) {
			if(arg=="test-build") {
				ConfigManager.testBuild = true
				ConfigManager.aggregatorS3ProbeIntervalMinutes = 1
				ConfigManager.minClientsForAggregation = 1000
				ConfigManager.nextRoundStartIntervalHours = 0.05
			}
		}
		ActorSystem[SimulatorSupervisor.Command](SimulatorSupervisor(), "nimble-fl-simulator")
	}
}
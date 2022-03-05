package org.nimbleedge.recoedge

import scala.concurrent.duration._

import akka.actor.testkit.typed.scaladsl.ScalaTestWithActorTestKit
import org.scalatest.wordspec.AnyWordSpecLike

class FLSystemManagerSpec extends ScalaTestWithActorTestKit with AnyWordSpecLike {
	import models._
	import FLSystemManager._

    /*
	It will be used for testing.
    The graphical structure of the topology below

        O1
         ├── A1
         │   ├── T1
         │   └── T2
         |
         └── A2
             ├── T3
             ├── T4
             └── A3
                 ├── T5 
                 └── T6

    */
    val o1 = OrchestratorIdentifier("O1")
    val a1 = AggregatorIdentifier(o1, "A1")
    val a2 = AggregatorIdentifier(o1, "A2")
    val a3 = AggregatorIdentifier(a2, "A3")
    val t1 = TrainerIdentifier(a1, "T1")
    val t2 = TrainerIdentifier(a1, "T2")
    val t3 = TrainerIdentifier(a2, "T3")
    val t4 = TrainerIdentifier(a2, "T4")
    val t5 = TrainerIdentifier(a3, "T5")
    val t6 = TrainerIdentifier(a3, "T6")

	"FLSystemManager actor" must {
		"be able to register a trainer, orchestrator and aggregator" in {
			val managerActor = spawn(FLSystemManager())

			// Create Trainer Actors
			val trainerProbe = createTestProbe[TrainerRegistered]()

			managerActor ! RequestTrainer(100, t5, trainerProbe.ref)
			val registered1 = trainerProbe.receiveMessage()
			registered1.requestId should ===(100)
			val trainerActor5 = registered1.actor

			managerActor ! RequestTrainer(101, t3, trainerProbe.ref)
			val registered2 = trainerProbe.receiveMessage()
			registered2.requestId should ===(101)
			val trainerActor3 = registered2.actor

			trainerActor5 should !==(trainerActor3)

			// Create Aggregators
			val aggProbe = createTestProbe[AggregatorRegistered]()

			managerActor ! RequestAggregator(102, a1, aggProbe.ref)
			val registered3 = aggProbe.receiveMessage()
			registered3.requestId should ===(102)
			val aggActor1 = registered3.actor

			managerActor ! RequestAggregator(103, a2, aggProbe.ref)
			val registered4 = aggProbe.receiveMessage()
			registered4.requestId should ===(103)
			val aggActor2 = registered4.actor

			aggActor1 should !==(aggActor2)

			// Test RealTimeGraph
			val realTimeGraphProbe = createTestProbe[RespondRealTimeGraph]()

			managerActor ! RequestRealTimeGraph(104, Left(o1), realTimeGraphProbe.ref)
			val registered5 = realTimeGraphProbe.receiveMessage(35.seconds)
			val expectedTree = Node(
				Left(o1), Set(
					Node(Right(a1), Set.empty),
					Node(Right(a2), Set(
						Leaf(t3),
						Node(Right(a3), Set(
							Leaf(t5)))))))
			registered5.realTimeGraph should ===(expectedTree)

			// TODO
			// add more tests here
		}

		// TODO
		// Add more FLSystemManager tests
	}
	// TODO
	// Add FLSystemManager tests here
}
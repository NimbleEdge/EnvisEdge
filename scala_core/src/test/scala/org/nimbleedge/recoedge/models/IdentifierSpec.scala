package org.nimbleedge.recoedge.models

import akka.actor.testkit.typed.scaladsl.ScalaTestWithActorTestKit
import org.scalatest.wordspec.AnyWordSpecLike

class IdentifierSpec extends ScalaTestWithActorTestKit with AnyWordSpecLike {

    /*
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


    /*
    The graphical structure of the topology below

        O2
         ├── A21
         │   ├── T21
         │   └── A23
         |       ├── T23 
         |       └── T24
         |
         └── A22
             ├── T22
             └── T25

    */
    val o2 = OrchestratorIdentifier("O2")
    val a21 = AggregatorIdentifier(o2, "A21")
    val a22 = AggregatorIdentifier(o2, "A22")
    val a23 = AggregatorIdentifier(a21, "A23")
    val t21 = TrainerIdentifier(a21, "T21")
    val t22 = TrainerIdentifier(a22, "T22")
    val t23 = TrainerIdentifier(a23, "T23")
    val t24 = TrainerIdentifier(a23, "T24")
    val t25 = TrainerIdentifier(a22, "T25")

	"Orchestrator Identifier" must {
		"have string representation equal to its name" in {
			o1.toString() should ===("O1")
			o2.toString() should ===("O2")
		}

		"return a singleton list with toList function" in {
			val o1toList = o1.toList()
			o1toList.size should ===(1)
			o1toList.head match {
				case result @ OrchestratorIdentifier(x) => x should ===("O1")
				case _ => fail("Expecting an Orchestrator Identifier, got different type")
			}

			val o2toList = o2.toList()
			o2toList.size should ===(1)
			o2toList.head match {
				case result @ OrchestratorIdentifier(x) => x should ===("O2")
				case _ => fail("Expecting an Orchestrator Identifier, got different type")
			}
		}	

		"should have the correctly populated list of children" in {
			val o1Children = o1.getChildren()
			o1Children.size should ===(2)
			o1Children should contain only (a1, a2)

			val o2Children = o2.getChildren()
			o2Children.size should ===(2)
			o2Children should contain only (a21, a22)
		}
	}

	"Aggregator Identifier" must {
		"have string representation equal to node path in tree" in {
            // A1 and A2 are similar
            val a1toString = a1.toString()
            a1toString should startWith ("O1 ")
            a1toString should endWith (" A1")

            // Testing A3
            val a3toString = a3.toString()
            a3toString should startWith ("O1 ")
            a3toString should include (" A2 ")
            a3toString should endWith (" A3")

            // Testing A23
            val a23toString = a23.toString()
            a23toString should startWith ("O2 ")
            a23toString should include (" A21 ")
            a23toString should endWith (" A23")
		}

        // TODO
        // Add more Aggregator Identifier tests
	}

	// TODO
	// Add Trainer Identifier tests here
}
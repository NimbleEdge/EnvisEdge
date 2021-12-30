package org.nimbleedge.recoedge

import models._

object Main {
    def main(args: Array[String]) = {
        val o1 = OrchestratorIdentifier("O1")
        val a1 = AggregatorIdentifier(o1, "A1")
        val a2 = AggregatorIdentifier(o1, "A2")
        val a3 = AggregatorIdentifier(a1, "A3")
        val t1 = TrainerIdentifier(a1, "T1")
        val t2 = TrainerIdentifier(a2, "T2")
        val t3 = TrainerIdentifier(a3, "T3")
        val t4 = TrainerIdentifier(a3, "T4")
        val t5 = TrainerIdentifier(a2, "T5")

        val o2 = OrchestratorIdentifier("O2")
        val a21 = AggregatorIdentifier(o2, "A21")
        val a22 = AggregatorIdentifier(o2, "A22")
        val a23 = AggregatorIdentifier(a21, "A23")
        val t21 = TrainerIdentifier(a21, "T21")
        val t22 = TrainerIdentifier(a22, "T22")
        val t23 = TrainerIdentifier(a23, "T23")
        val t24 = TrainerIdentifier(a23, "T24")
        val t25 = TrainerIdentifier(a22, "T25")

        println(t1.toString())
        println(t2.toString())
        println(t3.toString())
        println(t4.toString())
        println(t5.toString())

        println(t21.toString())
        println(t22.toString())
        println(t23.toString())
        println(t24.toString())
        println(t25.toString())
        println(t22.toList())

        println(a1.children)
    }
}
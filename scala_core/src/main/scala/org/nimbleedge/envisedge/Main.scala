package org.nimbleedge.envisedge

import models._
import akka.actor.typed.{ActorSystem, ActorRef, Behavior}
import akka.actor.typed.scaladsl.Behaviors
import akka.NotUsed

import scala.collection.mutable.{Map => MutableMap, ListBuffer}

object HostServer {
    // import FLSystemManager._
    import Aggregator._
    import FLSystemManager._

    def apply() : Behavior[NotUsed] = Behaviors.setup { context =>
        //val fl_system_manager = context.spawn(FLSystemManager(),"fl-system-manager")
        //fl_system_manager ! StartCycle(1)

        // val o2 = OrchestratorIdentifier("O2")
        // val a22 = AggregatorIdentifier(o2, "A22")
        // val t22 = TrainerIdentifier(a22, "T22")
        // val t25 = TrainerIdentifier(a22, "T25")

        // val aggregator = context.spawn(Aggregator(a22),"aggregator")
        // aggregator ! StartCycle(1)
        Behaviors.same
    }
} 

object Main {
    def main(args: Array[String]): Unit = {

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
        // val o1 = OrchestratorIdentifier("O1")
        // val a1 = AggregatorIdentifier(o1, "A1")
        // val a2 = AggregatorIdentifier(o1, "A2")
        // val a3 = AggregatorIdentifier(a2, "A3")
        // val t1 = TrainerIdentifier(a1, "T1")
        // val t2 = TrainerIdentifier(a1, "T2")
        // val t3 = TrainerIdentifier(a2, "T3")
        // val t4 = TrainerIdentifier(a2, "T4")
        // val t5 = TrainerIdentifier(a3, "T5")
        // val t6 = TrainerIdentifier(a3, "T6")

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
        // val a21 = AggregatorIdentifier(o2, "A21")
        val a22 = AggregatorIdentifier(o2, "A22")
        // val a23 = AggregatorIdentifier(a21, "A23")
        // val t21 = TrainerIdentifier(a21, "T21")
        val t22 = TrainerIdentifier(a22, "T22")
        // val t23 = TrainerIdentifier(a23, "T23")
        // val t24 = TrainerIdentifier(a23, "T24")
        val t25 = TrainerIdentifier(a22, "T25")

        // println(t1.toString())
        // println(t2.toString())
        // println(t3.toString())
        // println(t4.toString())
        // println(t5.toString())

        // println(t21.toString())
        // println(t22.toString())
        // println(t23.toString())
        // println(t24.toString())
        // println(t25.toString())
        // println(t22.toList())

        // println(a2.getChildren())
        //ActorSystem(HostServer(), "host-server")

        RedisClientHelper.initConnection()

        val map = Map("name" -> "Android", "clientId" -> "client-1", "aggId" -> "agg-1", "orcId" -> "orc-1" ,"cycleAccepted" -> 1)
        val map2 = Map("name" -> "IOS", "clientId" -> "client-2", "aggId" -> "agg-1", "orcId" -> "orc-1" ,"cycleAccepted" -> 0)
        RedisClientHelper.hmset("device-1", map)
        RedisClientHelper.hmset("device-2", map2)

        RedisClientHelper.lpush("agg-1", "client-1")
        RedisClientHelper.rpush("agg-1", "client-2")

        println(RedisClientHelper.getList("agg-1").toList.flatten.flatten)

        println(RedisClientHelper.hmget("device-1", "name", "clientId", "aggId", "orcId"))

        RedisClientHelper.flushdb()
    }
}
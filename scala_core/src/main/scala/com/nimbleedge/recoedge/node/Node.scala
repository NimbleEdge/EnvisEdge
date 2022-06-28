package com.nimbleedge.recoedge.node

import akka.actor.{Actor, ActorRef, Props}
import com.nimbleedge.recoedge.node.Node._
import com.nimbleedge.recoedge.node.cluster.ClusterManager.GetMembers
import com.nimbleedge.recoedge.processors.FLSystemManager
import com.nimbleedge.recoedge.processors.FLSystemManager._
import com.nimbleedge.recoedge.processors.responses.APIObjects.RequestNetwork
object Node {

  sealed trait NodeMessage

  case class GetFibonacci(n: Int)
//  case class CreateOrchestratorNode(n : Int )

  case class CreateNetwork( n : RequestNetwork )
  case class CreateOrchestrator( n:String )
  case class CheckOrchestrator(n:String)
  case class DeleteOrchestrator(n:String)
  case class CreateAggregator(orcId:String, aggId : String )
  case class CreateAggregators(orcId:String, aggIds : String )
  case class CheckAggregator(orcId:String, aggId : String )
  case class CheckAggregators(orcId:String, aggIds : String )
  case class DeleteAggregator(n:String)
  case class CreateTrainer(n:String)
  case class CheckTrainer(n:String)
  case class DeleteTrainer(n:String)

  case object GetClusterMembers

  def props(nodeId: String) = Props(new Node(nodeId))
}

class Node(nodeId: String) extends Actor {

//  val processor: ActorRef = context.actorOf(processor.Processor.props(nodeId), "processor")
//  val processorRouter: ActorRef = context.actorOf(FromConfig.props(Props.empty), "processorRouter")
  val clusterManager: ActorRef = context.actorOf(cluster.ClusterManager.props(nodeId), "clusterManager")
  val flCoreSystemManager = context.actorOf(FLSystemManager.props( nodeId), "flCoreSystemManager")


//  val flCoreSystemManager = context.spawn(FLCoreSystemManager(), "flCoreSystemManager")

  override def receive: Receive = {
    case GetClusterMembers => clusterManager forward GetMembers
//    case GetFibonacci(value) => processorRouter forward ComputeFibonacci(value)

    case CreateNetwork(value) => flCoreSystemManager forward CreateNetworkFLCommand(value)

//    case CreateOrchestratorNode(value) => processorRouter forward CreateOrchestratorProcessor(value)
    case CreateOrchestrator(value) => flCoreSystemManager forward CreateOrchestratorFLCommand(value)
    case CheckOrchestrator(value) => flCoreSystemManager forward OrchestratorFLHealthCheck(value)
    case DeleteOrchestrator(value) => flCoreSystemManager forward DeleteOrchestratorFLCommand(value)
    case CreateAggregator(orcId, aggId ) => flCoreSystemManager forward CreateAggregatorFLCommand(orcId, aggId )
    case CheckAggregator(orcId, aggId)  => flCoreSystemManager forward AggregatorFLHealthCheck(orcId, aggId )
    case CreateAggregators(orcId, aggIds ) => flCoreSystemManager forward CreateAggregatorsFLCommand(orcId, aggIds )
    case CheckAggregators(orcId, aggIds)  => flCoreSystemManager forward AggregatorsFLHealthCheck(orcId, aggIds )

//    case DeleteAggregator(value) => flCoreSystemManager forward DeleteAggregatorCommand(value)
//    case CreateTrainer(value) => flCoreSystemManager forward CreateTrainerCommand(value)
//    case CheckTrainer(value) => flCoreSystemManager forward TrainerHealthCheck(value)
//    case DeleteTrainer(value) => flCoreSystemManager forward DeleteTrainerCommand(value)



  }
}

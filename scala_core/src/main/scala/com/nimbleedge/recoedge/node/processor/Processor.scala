//package com.nimbleedge.recoedge.node.processor
//
//import akka.actor.{Actor, ActorRef, Props}
//import com.nimbleedge.recoedge.node.processor.actors.ProcessorFibonacci.Compute
//
//object Processor {
//
//  sealed trait ProcessorMessage
//
//  case class ComputeFibonacci(n: Int) extends ProcessorMessage
////  case class CreateOrchestratorProcessor(n:String) extends ProcessorMessage
//
//  def props(nodeId: String) = Props(new Processor(nodeId))
//}
//
//class Processor(nodeId: String) extends Actor {
//  import Processor._
//
//  val fibonacciProcessor: ActorRef = context.actorOf(actors.ProcessorFibonacci.props(nodeId), "fibonacci")
////  val orchestratorProcessor: ActorRef = context.actorOf(Orchestrator.props(nodeId), "orchestrator")
//
//  override def receive: Receive = {
//    case ComputeFibonacci(value) => {
//      val replyTo = sender()
//      fibonacciProcessor ! Compute(value, replyTo)
//    }
//  }
//}

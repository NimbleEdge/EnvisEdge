package com.nimbleedge.recoedge.actors


import akka.actor.{Actor, ActorRef, Props}
import akka.event.Logging
import akka.pattern.ask
import akka.util.Timeout
import com.nimbleedge.recoedge.actors.Aggregator.{CreateAggregatorTrainerCommand, CreateChildAggregatorCommand, CreateTrainerCommand}
import com.nimbleedge.recoedge.identifiers.TrainerIdentifier
import com.nimbleedge.recoedge.processors.responses.ProcessorFLManagerResponse
//import com.nimbleedge.recoedge.actors.Aggregator.CreateChildAggregator
import com.nimbleedge.recoedge.identifiers.{AggregatorIdentifier, Identifier, OrchestratorIdentifier}
import com.nimbleedge.recoedge.processors.FLSystemManager.ActorRegistered
import com.nimbleedge.recoedge.processors.responses.APIObjects

import scala.collection.mutable.{ListBuffer, Map => MutableMap}
import scala.concurrent.Await
import scala.concurrent.duration._


object Orchestrator {
  // TODO Need to add state
  sealed trait Command
  case class TestOrchestratorCommand( n:String , orcId : OrchestratorIdentifier , replyTo: ActorRef) extends Command
  case class CreateAggregatorCommand( n:String , aggId: AggregatorIdentifier, replyTo: ActorRef) extends Command
  case class CreateAggregatorsLevelOneCommand( requestId :String , aggIds : List[AggregatorIdentifier] ,
                                               trainerIds : List[TrainerIdentifier],
                                               replyTo : ActorRef ) extends Command
  case class CreateAggregatorsCommand( n:String , orcId : OrchestratorIdentifier , aggId: String, replyTo: ActorRef) extends Command

  case class CheckAggregatorCommand( n:String , aggId: AggregatorIdentifier, replyTo: ActorRef) extends Command

  case class CreateOrchestratorNetworkCommand( requestId:String , orchestrator : APIObjects.Orchestrator , replyTo:ActorRef ) extends Command

  def props(nodeId: OrchestratorIdentifier) = Props(new Orchestrator(nodeId))

}

class Orchestrator(orcId: OrchestratorIdentifier) extends Actor {

  import Orchestrator._
  val log = Logging(context.system, this)

  override def preStart() = {
    log.debug("Starting Orchestrator")
    log.info("Starting Orchestrator::info")

  }

  implicit lazy val timeout = Timeout(5.seconds)
  //  // TODO
  //  // Add state and persistent information
    var aggIdToRef : MutableMap[AggregatorIdentifier, ActorRef] = MutableMap.empty

    private def getAggregatorRef(aggId: AggregatorIdentifier): ActorRef = {
      aggIdToRef.get(aggId) match {
        case Some(actorRef) =>
          actorRef
        case None =>
          log.info("Creating new aggregator actor for {}", aggId.name())
          val actorRef = context.actorOf(Aggregator.props(aggId), s"aggregator-${aggId.name()}")
//          context.watchWith(actorRef, AggregatorTerminated(actorRef, aggId))
          aggIdToRef += aggId -> actorRef
          actorRef
      }
    }

    private def getAggregatorsRef( aggIds : List[AggregatorIdentifier] ) :  MutableMap[String, ActorRef]  = {
      var mapAggIdentifierToRef :MutableMap[String, ActorRef] = MutableMap.empty
      for ( aggId <- aggIds ) {
        var aggRef = getAggregatorRef(aggId )
        mapAggIdentifierToRef += aggId.id -> aggRef
      }
      mapAggIdentifierToRef
    }


  override def receive: Receive = {

    case TestOrchestratorCommand(value, orcId , replyTo) =>
      replyTo ! ProcessorFLManagerResponse(value, orcId.name, "40")


    case CreateAggregatorCommand(requestId , aggId, replyTo) => {
      val actorRef = getAggregatorRef(aggId)
      log.info( "SUCCESS::AGGREGATOR CREATED :: " + aggId.name() )
      replyTo ! ActorRegistered(requestId, actorRef)
    }

    case CreateOrchestratorNetworkCommand( requestId , orchestrator,replyTo ) => {
      log.info( "CreateOrchestratorNetworkCommand called :: " )
      val identifier = OrchestratorIdentifier( orchestrator.name )
      var aggs = orchestrator.aggregators
      if ( aggs == null || aggs.isEmpty ) {
        replyTo ! ProcessorFLManagerResponse(requestId, "Empty Aggregators", "Empty Aggregators")
      }
      else {
        for ( agg <- aggs ) {
          val aggId = AggregatorIdentifier( identifier , agg.aggname )
          val ref = getAggregatorRef( aggId )
          log.info( "CreateOrchestratorNetworkCommand :: Calling CreateAggregatorTrainerCommand " + agg.aggname )

          ref ? CreateAggregatorTrainerCommand( requestId, agg, identifier, replyTo )
        }
      }

    }

    case CreateAggregatorsLevelOneCommand(requestId,aggIds,trainerIds, replyTo)=> {
      log.info( "CreateAggregatorsLevelOneCommand called :: " )
      val mapAggIdToRef  = getAggregatorsRef( aggIds )

      for ( trainer <- trainerIds ) {
        val aggId = trainer.parentIdentifier.asInstanceOf[AggregatorIdentifier].id
        mapAggIdToRef.get( aggId ) match {
          case Some(ref) =>
            ref ! CreateTrainerCommand( requestId, trainer, ref )
        }
      }

      replyTo !  ProcessorFLManagerResponse(requestId ,"Create multiple aggregators" , "DONE")
    }


    case CheckAggregatorCommand(requestId, aggId, replyTo ) => {
      aggIdToRef.get(aggId) match {
        case None =>
          replyTo ! ProcessorFLManagerResponse(requestId, aggId.name(), "AGGREGATOR " + aggId.name() + " NOT FOUND")
        case Some(ref) =>
          ref ! ProcessorFLManagerResponse(requestId, aggId.name(), "OK")
      }
    }


    case CreateAggregatorsCommand(requestId , orcId , aggIds, replyTo) => {
      var aggregatorIdentifiers : Array[String] = aggIds.split("/")
      //
      var parentIdentifier: Identifier = orcId
      var actorReference:ActorRef = Actor.noSender
      for( strAggIdentifier <- aggregatorIdentifiers)  {
        var aggIdentifier  = AggregatorIdentifier(parentIdentifier, strAggIdentifier)
        parentIdentifier match {
          case _: OrchestratorIdentifier =>
            actorReference = getAggregatorRef( aggIdentifier )
          case _: AggregatorIdentifier =>
            val future  =  actorReference ? CreateChildAggregatorCommand(requestId,  aggIdentifier, replyTo )
            val result = Await.result(future, timeout.duration).asInstanceOf[ActorRegistered]
            actorReference = result.actor
            parentIdentifier = aggIdentifier
        }
      }
      replyTo ! ProcessorFLManagerResponse(requestId, aggIds, "OK")
      }



  }
}

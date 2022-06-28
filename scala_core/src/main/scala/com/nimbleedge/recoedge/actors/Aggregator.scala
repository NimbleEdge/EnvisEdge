package com.nimbleedge.recoedge.actors


//import models._
import akka.actor.{Actor, ActorRef, Props}
import akka.event.Logging
import com.nimbleedge.recoedge.identifiers.{AggregatorIdentifier, Identifier, TrainerIdentifier}
import com.nimbleedge.recoedge.processors.FLSystemManager.{ActorRegistered, ActorsRegistered}
import com.nimbleedge.recoedge.processors.responses.ProcessorFLManagerResponse
import com.nimbleedge.recoedge.processors.responses.APIObjects

import scala.collection.mutable.{ListBuffer, Map => MutableMap}
import akka.pattern.ask
import akka.util.Timeout
import com.nimbleedge.recoedge.actors.Trainer.TrainerProducerConsumerMessage

import scala.concurrent.duration._


object Aggregator {
  sealed trait Command
  case class TestAggregatorCommand( n:String , aggId : AggregatorIdentifier , replyTo: ActorRef) extends Command
  case class CreateChildAggregatorCommand( n:String, aggId :AggregatorIdentifier , replyTo: ActorRef) extends Command
  case class CreateTrainerCommand( n:String, trainerId : TrainerIdentifier , replyTo: ActorRef) extends Command
  case class CheckTrainerCommand( n:String, trainerId:TrainerIdentifier, replyTo:ActorRef ) extends Command
  case class CreateNetworkTrainersCommand( n:String, trainerIds: List[TrainerIdentifier]  , replyTo: ActorRef) extends Command
  case class CreateAggregatorTrainerCommand( requestId:String, aggregator:APIObjects.Aggregators, identifier:Identifier , replyTo: ActorRef) extends Command

  def props( nodeId: AggregatorIdentifier) = Props(new Aggregator(nodeId ))
//  // In case of any Trainer / Aggregator (Child) Termination
  private final case class AggregatorTerminated(actor: ActorRef, aggId: AggregatorIdentifier)
    extends Aggregator.Command
//
  private final case class TrainerTerminated(actor: ActorRef, traId: TrainerIdentifier) extends Command

  // TODO
  // Add messages here
}

class Aggregator(aggId: AggregatorIdentifier) extends Actor {
  import Aggregator._
  val log = Logging(context.system, this)
  override def preStart() = {
    log.info("Starting Aggregator::info")
 }
//  import FLSystemManager.{ RequestTrainer, TrainerRegistered, RequestAggregator, AggregatorRegistered, RequestRealTimeGraph }

  // TODO
  // Add state and persistent information

  // List of Aggregators which are children of this aggregator
  var aggregatorIdsToRef : MutableMap[AggregatorIdentifier, ActorRef] = MutableMap.empty

//  // List of trainers which are children of this aggregator
  var trainerIdsToRef : MutableMap[TrainerIdentifier, ActorRef] = MutableMap.empty
//
//  context.log.info("Aggregator {} started", aggId.toString())
//
  def getTrainerRef(trainerId: TrainerIdentifier): ActorRef = {
    trainerIdsToRef.get(trainerId) match {
      case Some(actorRef) =>
        // Need to check whether the trainer parent is valid or not using aggId
        actorRef
      case None =>
        log.info("Creating new Trainer actor for {}", trainerId.toString())
        val actorRef = context.actorOf(Trainer.props(trainerId), s"trainer-${trainerId.name()}")
        context.watchWith(actorRef, TrainerTerminated(actorRef, trainerId))

        trainerIdsToRef += trainerId -> actorRef
        actorRef
    }
  }

  private def getTrainersRef( trainerIds : List[TrainerIdentifier] ) :List[ActorRef]  = {
    var output = new ListBuffer[ActorRef]()
    for ( trainerId <- trainerIds ) {
      val trainerRef = getTrainerRef(trainerId )
      output += trainerRef
    }
    output.toList
  }

  def getAggregatorRef( aggregatorId: AggregatorIdentifier): ActorRef = {
    aggregatorIdsToRef.get(aggregatorId) match {
      case Some(actorRef) =>
        actorRef
      case None =>
        log.info("Creating new Aggregator actor for {}", aggregatorId.toString())
        val actorRef = context.actorOf(Aggregator.props(aggregatorId), s"aggregator-${aggregatorId.name()}")
        context.watchWith(actorRef, AggregatorTerminated(actorRef, aggregatorId))
        aggregatorIdsToRef += aggregatorId -> actorRef
        actorRef
    }
  }

  override def receive: Receive = {
    case TestAggregatorCommand(value, aggId , replyTo) =>
      replyTo ! ProcessorFLManagerResponse(value, aggId.name, "40")

    case CreateTrainerCommand( requestId, trainerId  , replyTo) =>
      val actorRef = getTrainerRef(trainerId )
      replyTo ! ActorRegistered(requestId, actorRef)

    case CreateChildAggregatorCommand( requestId , aggId, replyTo ) => {
      val actorRef = getAggregatorRef(aggId)
      replyTo ! ActorRegistered(requestId, actorRef)
    }
    case CreateNetworkTrainersCommand( requestId ,trainerIds,replyTo) => {
      val actorRefs = getTrainersRef(trainerIds)
      replyTo ! ActorsRegistered( requestId , actorRefs )

    }
    case CreateAggregatorTrainerCommand( requestId, aggregator, identifier, replyTo ) => {
      implicit val timeout = Timeout(10 seconds)
      val aggs : List[APIObjects.Aggregators] =  aggregator.aggregators
        if ( aggs == null || aggs.isEmpty ) {
          // Check if there are any trainers
          if ( aggregator.trainers != null && !aggregator.trainers.isEmpty ) {
            for ( trainer <- aggregator.trainers ) {
              var trainerRef = getTrainerRef(TrainerIdentifier( aggId, trainer.trainerid ))
              log.info( "CreateAggregatorTrainerCommand :: Create Trainer " + trainer.trainerid + " :: Created  " )
              trainerRef ? TrainerProducerConsumerMessage( requestId, trainer.message, replyTo )
            }
          }

          replyTo ! ProcessorFLManagerResponse(requestId, "Empty Agg", "Empty Agg")
        }
        else {
          for ( agg <- aggs ) {
            val aggId = AggregatorIdentifier( identifier , agg.aggname  )
            var ref = getAggregatorRef( aggId )
            log.info( "CreateAggregatorTrainerCommand :: Create Aggregator " + agg.aggname + " :: Created  " )
            ref ? CreateAggregatorTrainerCommand ( requestId, agg, aggId, replyTo)
            if ( agg.trainers != null && !agg.trainers.isEmpty ) {
              for ( trainer <- agg.trainers ) {
                var trainerRef = getTrainerRef(TrainerIdentifier( aggId, trainer.trainerid ))
                log.info( "CreateAggregatorTrainerCommand :: Create Trainer " + trainer.trainerid + " :: Created  " )
                trainerRef ? TrainerProducerConsumerMessage( requestId, trainer.message, replyTo )
              }
            }
          }
        }
    }
  }

}
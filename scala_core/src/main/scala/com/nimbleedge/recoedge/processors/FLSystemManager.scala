package com.nimbleedge.recoedge.processors

import akka.actor.{Actor, ActorRef, Props}
import akka.event.Logging
import akka.pattern.ask
import akka.util.Timeout
import com.nimbleedge.recoedge.actors.Orchestrator
import com.nimbleedge.recoedge.actors.Orchestrator._
import com.nimbleedge.recoedge.identifiers.{AggregatorIdentifier, OrchestratorIdentifier, TrainerIdentifier, Identifier}
import com.nimbleedge.recoedge.processors.responses.APIObjects.RequestNetwork
import com.nimbleedge.recoedge.processors.responses.ProcessorFLManagerResponse

import com.nimbleedge.recoedge.processors.responses.APIObjects

import java.util.UUID.randomUUID
import scala.collection.mutable.{ListBuffer, Map => MutableMap}
import scala.concurrent.duration.DurationInt



object FLSystemManager {
  sealed trait Command

  def props(nodeId: String) = Props(new FLSystemManager(nodeId))

  final case class CreateNetworkFLCommand(network: RequestNetwork)

  final case class CreateOrchestratorFLCommand(orcId: String) extends Command

  final case class OrchestratorFLHealthCheck(orcId: String) extends Command

  final case class DeleteOrchestratorFLCommand(orcId: String) extends Command

  // Aggregator Commands
  final case class CreateAggregatorFLCommand(orcId: String, aggId: String) extends Command

  final case class CreateAggregatorsFLCommand(orcId: String, aggIds: String) extends Command

  final case class ForceCreateAggregatorFLCommand(orcId: String, aggIds: String) extends Command

  final case class AggregatorFLHealthCheck(orcId: String, aggIds: String) extends Command

  final case class AggregatorsFLHealthCheck(orcId: String, aggIds: String) extends Command

  final case class DeleteAggregatorFLCommand(orcId: String, aggIds: String, aggId: String) extends Command

  // Trainer Commands
  final case class CreateTrainerFLCommand(orcId: String, aggIds: String, trainerId: String) extends Command

  final case class ForceCreateTrainerFLCommand(orcId: String, aggIds: String, trainerId: String) extends Command

  final case class TrainerFLHealthCheck(orcId: String, aggIds: String, trainerId: String) extends Command

  final case class DeleteTrainerFLCommand(orcId: String, aggIds: String, trainerId: String) extends Command

  // Placeholders
  final case class ActorRegistered(requestId: String, actor: ActorRef)

  final case class ActorsRegistered(requestId: String, actors: List[ActorRef])


  // FLSystemManager would be treated like a processor
  class FLSystemManager(nodeId: String) extends Actor {

//    import FLSystemManager._

    implicit lazy val timeout = Timeout(20.seconds)

    val log = Logging(context.system, this)

    override def preStart() = {
      log.debug("Starting FLSystemManager")
      log.info("Starting FLSystemManager::info")

    }

    var orcIdToRef: MutableMap[OrchestratorIdentifier, ActorRef] = MutableMap.empty

    def getAggregators( orchestrator: APIObjects.Orchestrator ) : ( ListBuffer[AggregatorIdentifier], ListBuffer[TrainerIdentifier])  = {
      var aggIdentifiers: ListBuffer[AggregatorIdentifier] = ListBuffer[AggregatorIdentifier]()
      var trainerIdentifiers: ListBuffer[TrainerIdentifier] = ListBuffer[TrainerIdentifier]()

      def getAggr( aggs :List[APIObjects.Aggregators] , identifier : Identifier ) :Unit = {
        if ( aggs == null || aggs.isEmpty ) {}
        else {
          for ( agg <- aggs ) {
            val aggId = AggregatorIdentifier( identifier , agg.aggname )
            aggIdentifiers += AggregatorIdentifier( identifier , agg.aggname )
            getAggr( agg.aggregators, aggId )
            if ( agg.trainers != null && !agg.trainers.isEmpty ) {
              for ( trainer <- agg.trainers ) {
                trainerIdentifiers += TrainerIdentifier( aggId, trainer.trainerid )
              }
            }
          }
        }
      }

      getAggr( orchestrator.aggregators, OrchestratorIdentifier(orchestrator.name) )
      (aggIdentifiers, trainerIdentifiers )
    }

    private def getOrchestratorRef(orcId: OrchestratorIdentifier): ActorRef = {
      orcIdToRef.get(orcId) match {
        case Some(actorRef) =>
          actorRef
        case None =>
          //          context.log.info("Creating new orchestrator actor for {}", orcId.name())
          val actorRef = context.actorOf(Orchestrator.props(orcId), s"orchestrator-${orcId.name()}")
          //        context.watchWith(actorRef, OrchestratorTerminated(actorRef, orcId))
          orcIdToRef += orcId -> actorRef
          actorRef
      }
    }


    override def receive: Receive = {
      case CreateOrchestratorFLCommand(orcId) => {
        val replyTo = sender()
        val orchestratorId = OrchestratorIdentifier(orcId)
        val actorRef = getOrchestratorRef(orchestratorId)
        val requestId = randomUUID().toString()
        replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name(), "OK")
      }
      case OrchestratorFLHealthCheck(orcId) => {
        val replyTo = sender()
        val orchestratorId = OrchestratorIdentifier(orcId)
        val requestId = randomUUID().toString()
        orcIdToRef.get(orchestratorId) match {
          case Some(ref) =>
            ref ! TestOrchestratorCommand(requestId, orchestratorId, replyTo)
          case None =>
            replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name, "FAILED")
        }
      }
      case DeleteOrchestratorFLCommand(orcId) => {}

      case CreateAggregatorFLCommand(orcId, aggId) => {
        val replyTo = sender()
        val orchestratorId = OrchestratorIdentifier(orcId)
        val requestId = randomUUID().toString()
        var arrAggIds: Array[String] = aggId.split(":")
        if (arrAggIds.size == 1) {
          orcIdToRef.get(orchestratorId) match {
            case Some(ref) =>
              ref ! CreateAggregatorCommand(requestId, AggregatorIdentifier(orchestratorId, aggId), replyTo)
            case None =>
              replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name, "FAILED::ORCHESTRATOR NOT FOUND")
          }
        }
        else {
          replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name, "FAILED::TOO MANY AGG IDS")
        }
      }

      case AggregatorFLHealthCheck(orcId, aggId) => {
        val replyTo = sender()
        val orchestratorId = OrchestratorIdentifier(orcId)
        val requestId = randomUUID().toString()
        orcIdToRef.get(orchestratorId) match {
          case Some(ref) =>
            val aggregatorIdentifier = AggregatorIdentifier(orchestratorId, aggId)
            ref ! CheckAggregatorCommand(requestId, aggregatorIdentifier, replyTo)
          case None =>
            replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name, "FAILED::UNABLE TO FIND ORCHESTRATOR")
        }
      }

      case CreateAggregatorsFLCommand(orcId, aggIds) => {
        val replyTo = sender()
        val orchestratorId = OrchestratorIdentifier(orcId)
        val requestId = randomUUID().toString()
        orcIdToRef.get(orchestratorId) match {
          case Some(ref) =>
            ref ! CreateAggregatorsCommand(requestId, orchestratorId, aggIds, replyTo)
          case None =>
            replyTo ! ProcessorFLManagerResponse(requestId, orchestratorId.name, "FAILED::ORCHESTRATOR NOT FOUND")
        }
      }
      case CreateNetworkFLCommand(network) => {
        log.info("Inside CreateNetworkFLCommand")
        val replyTo = sender()
        val requestId = randomUUID().toString()

        val orchestratorId = OrchestratorIdentifier(network.orchestrator.id)
        val orchestratorRef = getOrchestratorRef(orchestratorId)
//        var aggIds = new ListBuffer[AggregatorIdentifier]()
//        var trainerIds = new ListBuffer[TrainerIdentifier]()
//        for (aggregator <- network.orchestrator.aggregators) {
//          val aggIdentifier = AggregatorIdentifier(orchestratorId, aggregator.aggid)
//          for (trainer <- aggregator.trainers) {
//            val trainerIdentifier = TrainerIdentifier(aggIdentifier, trainer.trainerid)
//            trainerIds += trainerIdentifier
//          }
//          aggIds += aggIdentifier
//        }


//      Recursion 
//        val output = getAggregators(network.orchestrator)
//        val aggIds = output._1
//       val trainerIds = output._2

//        orchestratorRef ? CreateAggregatorsLevelOneCommand(requestId, aggIds.toList, trainerIds.toList, replyTo)
          orchestratorRef ? CreateOrchestratorNetworkCommand( requestId , network.orchestrator , replyTo )
      }
    }
  }
}
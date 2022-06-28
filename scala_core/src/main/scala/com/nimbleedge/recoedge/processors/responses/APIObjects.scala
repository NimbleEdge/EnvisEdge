package com.nimbleedge.recoedge.processors.responses

import spray.json._

object APIObjects {

  case class Message(requestid: String, msg: String)

  object MessageProtocol extends DefaultJsonProtocol {

    implicit object MessageFormat extends RootJsonFormat[Message] {
      def write(obj: Message):JsValue  = {
        JsObject(
          "requestid" -> Option( obj.requestid ).map(JsString(_)).getOrElse(JsNull),
          "msg" -> Option( obj.msg ).map(JsString(_)).getOrElse(JsNull)
        )
      }

      def read(json: JsValue): Message = {
        val fields = json.asJsObject.fields
        Message(
          fields("requestid").convertTo[String],
          fields("msg").convertTo[String]
        )
      }
    }
  }

  case class Trainers(trainerid: String, trainername: String, message: Message)

  import MessageProtocol._
  object TrainersProtocol extends DefaultJsonProtocol {

    implicit object TrainersFormat extends RootJsonFormat[Trainers] {
      def write(obj: Trainers) : JsValue = {
        JsObject(
          "trainerid" -> Option( obj.trainerid ).map(JsString(_)).getOrElse(JsNull),
          "trainername" -> Option( obj.trainername ).map(JsString(_)).getOrElse(JsNull),
          "message" -> obj.message.toJson
        )
      }

      def read(json: JsValue): Trainers = {
        val fields = json.asJsObject.fields
        Trainers(
          fields("trainerid").convertTo[String],
          fields("trainername").convertTo[String],
          fields("message").convertTo[Message]
        )
      }
    }
  }

  case class Aggregators(aggid: String, aggname: String, aggregators: List[Aggregators], trainers: List[Trainers])

  import TrainersProtocol._
  object AggregatorsProtocol extends DefaultJsonProtocol {

    implicit object AggregatorsFormat extends RootJsonFormat[Aggregators] {
//      def write(obj: Aggregators) : Nothing = ???
      def write(obj: Aggregators) :JsValue = {
        JsObject(
          "aggid" -> JsString( obj.aggid ),
          "aggname" -> JsString( obj.aggname ),
          "aggregators" -> obj.aggregators.toJson,
          "trainers" -> obj.trainers.toJson
        )
      }

      def read(json: JsValue): Aggregators = {
        val fields = json.asJsObject.fields
        if (fields.isDefinedAt( "aggregators") ) {
          val aggregatorsOpt: Option[List[Aggregators]] =  fields("aggregators").convertTo[Option[List[Aggregators]]]
          //          val aggOpt = aggregatorsOpt.orNull[List[Aggregators]]
          Aggregators(
            fields("aggid").convertTo[String],
            fields("aggname").convertTo[String],
            aggregatorsOpt.orNull[List[Aggregators]],
//            fields("aggregators").convertTo[List[Aggregators]],
            fields("trainers").convertTo[List[Trainers]])

        }
        else {
          Aggregators(
            fields("aggid").convertTo[String],
            fields("aggname").convertTo[String],
            List[Aggregators](),
            //            fields("aggregators").convertTo[Option[List[Aggregators]]],
            fields("trainers").convertTo[List[Trainers]])

        }
      }
    }
  }

  case class Orchestrator(name: String, id: String, aggregators: List[Aggregators])
  import AggregatorsProtocol._
  object OrchestratorProtocol extends DefaultJsonProtocol {

    implicit object OrchestratorFormat extends RootJsonFormat[Orchestrator] {
      def write(obj: Orchestrator) :JsValue = {
        JsObject(
          "name" -> Option( obj.name ).map(JsString(_)).getOrElse(JsNull),
          "id" -> Option( obj.id ).map(JsString(_)).getOrElse(JsNull),
          "aggregators" -> obj.aggregators.toJson
        )

      }

      def read(json: JsValue): Orchestrator = {
        val fields = json.asJsObject.fields
        Orchestrator(
          fields("name").convertTo[String],
          fields("id").convertTo[String],
          fields("aggregators").convertTo[List[Aggregators]]

        )
      }
    }
  }


  case class RequestNetwork(name: String, id: String, orchestrator: Orchestrator)

  import OrchestratorProtocol._
  object RequestNetworkProtocol extends DefaultJsonProtocol {

    implicit object RequestNetworkFormat extends RootJsonFormat[RequestNetwork] {
      def write(obj: RequestNetwork) :JsValue = {
        JsObject(
          "name" -> Option( obj.name ).map(JsString(_)).getOrElse(JsNull),
          "id" -> Option( obj.id ).map(JsString(_)).getOrElse(JsNull),
          "orchestrator" -> obj.orchestrator.toJson
        )
      }
//      def write(obj:RequestNetwork) : Nothing = ???

      def read(json: JsValue): RequestNetwork = {
        val fields = json.asJsObject.fields
        RequestNetwork(
          fields("name").convertTo[String],
          fields("id").convertTo[String],
          fields("orchestrator").convertTo[Orchestrator]

        )
      }
    }
  }
  // Request
  final case class RequestAndOrchestrator(requestId: String, orcId: String)
  final case class RequestOrchestratorAndAggregator(requestId: String, orcId: String, aggId:String )
  final case class RequestOrchestratorAndAggregators(requestId: String, orcId: String, aggIds:String )

  final case class RequestOrchestratorAggregatorAndTrainer(requestId: String, orcId: String, aggIds:String , trainerId :String )

  // Response
  sealed trait ExtResponses
  final case class ExtResponse(artifactId: Long, userId: String, answer: Option[Boolean], failureMsg: Option[String]) extends ExtResponses
  final case class AllStatesResponse(
                                      artifactId: Long,
                                      userId: String,
                                      artifactRead: Option[Boolean],
                                      artifactInUserFeed: Option[Boolean],
                                      failureMsg: Option[String]) extends ExtResponses
  final case class CommandResponse(success: Boolean) extends ExtResponses

}
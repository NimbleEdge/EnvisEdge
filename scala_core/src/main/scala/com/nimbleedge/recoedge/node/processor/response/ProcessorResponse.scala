package com.nimbleedge.recoedge.node.processor.response

import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport
import spray.json.DefaultJsonProtocol

final case class RequestAndOrchestratorId(requestId: String, orchestratorId: String)

case class ProcessorResponse(nodeId: String, result: BigInt)
//case class ProcessorOrchestratorResponse( requestId : String , orcheestratorIdentifier : OrchestratorIdentifier)
case class ProcessorFLManagerResponse(  requestId : String , orcId : String, result : String )

object ProcessorResponseJsonProtocol extends SprayJsonSupport with DefaultJsonProtocol{
  implicit val processorResponse = jsonFormat2(ProcessorResponse)
}

object ProcessorFLManagerResponseJsonProtocol extends SprayJsonSupport with DefaultJsonProtocol{
  implicit val processorFLManagerResponse = jsonFormat3(ProcessorFLManagerResponse)
}




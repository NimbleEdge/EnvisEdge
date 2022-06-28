package com.nimbleedge.recoedge.processors.responses


import com.nimbleedge.recoedge.processors.responses.APIObjects.RequestAndOrchestrator
import spray.json.DefaultJsonProtocol

object JsonFormats  {
  // import the default encoders for primitive types (Int, String, Lists etc)
  import DefaultJsonProtocol._

  implicit val orchestratorJsonFormat = jsonFormat2(RequestAndOrchestrator)
//  implicit val psResponse = jsonFormat4(ExtResponse)
//  implicit val psResponseII = jsonFormat5(AllStatesResponse)
//  implicit val cmdResponse = jsonFormat1(CommandResponse)

}

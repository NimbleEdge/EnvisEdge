package com.nimbleedge.recoedge.api

import akka.actor.{ActorRef, ActorSystem}
import akka.http.scaladsl.marshallers.sprayjson._
import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Directives.{pathPrefix, _}
import akka.http.scaladsl.server.Route
import akka.pattern.ask
import akka.util.Timeout
//import com.nimbleedge.recoedge.Server.aggregatorNetworkFormat
import com.nimbleedge.recoedge.node.Node._
import com.nimbleedge.recoedge.processors.responses.APIObjects._
import com.nimbleedge.recoedge.processors.responses.ProcessorFLManagerResponse
import spray.json.{DefaultJsonProtocol, NullOptions}

import scala.concurrent.Future
import scala.concurrent.duration._

trait NodeRoutes extends SprayJsonSupport with DefaultJsonProtocol with NullOptions {
  import com.nimbleedge.recoedge.processors.responses.APIObjects.RequestNetworkProtocol._
  import spray.json.{RootJsonFormat, _}


  //  implicit val clientJsonFormat: RootJsonFormat[Client] = jsonFormat5(Client)
  implicit val orchestratorJsonFormat: RootJsonFormat[RequestAndOrchestrator]  = jsonFormat2(RequestAndOrchestrator)
  implicit val aggregatorJsonFormat : RootJsonFormat[RequestOrchestratorAndAggregator]  = jsonFormat3(RequestOrchestratorAndAggregator)
  implicit val trainerJsonFormat: RootJsonFormat[RequestOrchestratorAggregatorAndTrainer]  = jsonFormat4(RequestOrchestratorAggregatorAndTrainer)


//implicit val messageNetworkFormat = lazyFormat( jsonFormat2( Message ))
//  implicit val trainerNetworkFormat = lazyFormat( jsonFormat3( Trainers ) )
//  implicit val aggregatorNetworkFormat = lazyFormat(jsonFormat3( Aggregators ))
//
//  implicit val aggregatorRecNetworkFormat :JsonFormat[AggregatorsRec] =
//    jsonFormat(AggregatorsRec, "aggid", "aggname", "aggregators")
//  implicit val orchestratorNetworkFormat = lazyFormat(jsonFormat3( Orchestrator ))
//  implicit val requestNetworkFormat : RootJsonFormat[RequestNetwork] = RequestNetworkFormat()


  implicit def system: ActorSystem

  def node: ActorRef

  implicit lazy val timeout = Timeout(5.seconds)

  lazy val nimbleOrchestratorRoutes: Route =
    pathPrefix("nimbleedge") {
      concat(
        // QUERIES:
        pathPrefix("orchestrator") {
          concat(
            get {
              parameters("orcId".as[String] ) { (orcId) =>
                val processFuture: Future[ProcessorFLManagerResponse] = (node ? CheckOrchestrator(orcId)).mapTo[ProcessorFLManagerResponse]
                onSuccess(processFuture) { response =>
                  complete(response.result)
                }
              }
            },
            post {
              entity(as[RequestAndOrchestrator]) { req =>
                val processFuture: Future[ProcessorFLManagerResponse] = (node ? CreateOrchestrator(req.orcId)).mapTo[ProcessorFLManagerResponse]
                onSuccess(processFuture) { response =>
                  complete(response.result )
                }
              }
            },
            pathPrefix("health") {
              concat(
                get {
                  parameters("orcId".as[String] ) { (orcId) =>
                    val processFuture: Future[ProcessorFLManagerResponse] = (node ? CheckOrchestrator(orcId)).mapTo[ProcessorFLManagerResponse]
                    onSuccess(processFuture) { response =>
                      complete(response.result)
                    }
                  }
                }

              )}
          )} ,
        pathPrefix( "aggregator") {
          concat(
          post {
            entity(as[RequestOrchestratorAndAggregator]) { req =>
              val processFuture: Future[ProcessorFLManagerResponse] = (node ? CreateAggregator(req.orcId, req.aggId)).mapTo[ProcessorFLManagerResponse]
              onSuccess(processFuture) { response =>
                complete(response.result )
              }
            }
          },
            pathPrefix("health") {
            concat(
              get {
                parameters("orcId".as[String], "aggId".as[String] ) { (orcId, aggId) =>
                  val processFuture: Future[ProcessorFLManagerResponse] = (node ? CheckOrchestrator(orcId)).mapTo[ProcessorFLManagerResponse]
                  onSuccess(processFuture) { response =>
                    complete(response.result)
                  }
                }
              }

            )}
          )


        } ,
        pathPrefix("network") {
          concat(
            post {
              entity(as[RequestNetwork]) { req =>
                val processFuture: Future[ProcessorFLManagerResponse] = (node ? CreateNetwork(req)).mapTo[ProcessorFLManagerResponse]
                onSuccess(processFuture) { response =>
                  complete(response.result )
                }
              }
            },
          )} ,

        pathPrefix("health") {
              concat(
                pathEnd {
                  concat(
                    get {
                      complete(StatusCodes.OK)

                    }
                  )
                }
              )
        }

      )
    }

//
//
//  lazy val psRoutes: Route =
//    pathPrefix("artifactState") {
//      concat(
//        // QUERIES:
//        pathPrefix("isArtifactReadByUser") {
//          concat(
//            get {
//              parameters("artifactId".as[Long], "userId") { (artifactId, userId) =>
//                complete {
//                  queryArtifactRead(ArtifactAndUser(artifactId, userId))
//                }
//              }
//            },
//            post {
//              entity(as[ArtifactAndUser]) { req =>
//                complete(StatusCodes.OK, queryArtifactRead(req))
//              }
//            })
//        },
//        pathPrefix("isArtifactInUserFeed") {
//          concat(
//            get {
//              parameters("artifactId".as[Long], "userId") { (artifactId, userId) =>
//                val req = ArtifactAndUser(artifactId, userId)
//                complete(queryArtifactInUserFeed(req))
//              }
//            },
//            post {
//              entity(as[ArtifactAndUser]) { req =>
//                complete(StatusCodes.OK, queryArtifactInUserFeed(req))
//              }
//            })
//        },
//        pathPrefix("getAllStates") {
//          concat(
//            get {
//              parameters("artifactId".as[Long], "userId") { (artifactId, userId) =>
//                val req = ArtifactAndUser(artifactId, userId)
//                complete(queryAllStates(req))
//              }
//            },
//            post {
//              entity(as[ArtifactAndUser]) { req =>
//                complete(StatusCodes.OK, queryAllStates(req))
//              }
//            })
//        },
//
//        // COMMANDS:
//        pathPrefix("setArtifactReadByUser") {
//          post {
//            entity(as[ArtifactAndUser]) { req =>
//              complete {
//                cmdArtifactRead(req)
//              }
//            }
//          }
//        },
//        pathPrefix("setArtifactAddedToUserFeed") {
//          post {
//            entity(as[ArtifactAndUser]) { req =>
//              complete {
//                cmdArtifactAddedToUserFeed(req)
//              }
//            }
//          }
//        },
//        pathPrefix("setArtifactRemovedFromUserFeed") {
//          post {
//            entity(as[ArtifactAndUser]) { req =>
//              complete {
//                cmdArtifactRemovedFromUserFeed(req)
//              }
//            }
//          }
//        })
//    }


//  lazy val nimbleRoute: Route = pathPrefix("nimbleedge") {
//    concat(
//      pathEnd {
//        concat(
//          path(IntNumber) { n =>
//            //          get {
//            //            complete(StatusCodes.OK)
//            //          }
//
//            get {
//              val processFuture: Future[ProcessorResponse] = (node ? CreateOrchestrator(n)).mapTo[ProcessorResponse]
//              onSuccess(processFuture) { response =>
//                complete(StatusCodes.OK, response)
//              }
//            }
//          }
//        )
//      }
//    )
//  }

//  lazy val nimbleRoute: Route = pathPrefix("nimbleedge") {
//    concat(
//      pathPrefix("orchestrator") {
//        concat(
//          path(IntNumber) { n =>
//            pathEnd {
//              concat(
//                get {
//                  val processFuture: Future[ProcessorFLManagerResponse] = (node ? CreateOrchestrator(n.toString())).mapTo[ProcessorFLManagerResponse]
//                  onSuccess(processFuture) { response =>
//                    complete(StatusCodes.OK)
//                  }
//                }
//              )
//            }
//
//
//          }
//        )
//      }
//    )
//  }


//  lazy val nimbleRoute1: Route = pathPrefix("xyz") {
//    concat(
//      pathPrefix("abc") {
//        concat(
//          path(IntNumber) { n =>
//            pathEnd {
//              concat(
//                get {
//                  val processFuture: Future[ProcessorFLManagerResponse] = (node ? CheckOrchestrator(n.toString())).mapTo[ProcessorFLManagerResponse]
//                  onSuccess(processFuture) { response =>
//                    complete(StatusCodes.OK)
//                  }
//                }
//              )
//            }
//
//
//          }
//        )
//      }
//    )
//  }
//


//  lazy val nimbleRoute1: Route = pathPrefix("health") {
//    concat(
//      pathEnd {
//        concat(
//          get {
//            complete(StatusCodes.OK)
//
//          }
//        )
//      }
//    )
//  }

  lazy val statusRoutes: Route = pathPrefix("status") {
    concat(
      pathPrefix("members") {
        concat(
          pathEnd {
            concat(
              get {
                val membersFuture: Future[List[String]] = (node ? GetClusterMembers).mapTo[List[String]]
                onSuccess(membersFuture) { members =>
                  complete(StatusCodes.OK, members)
                }
              }
            )
          }
        )
      }
    )
  }

//  lazy val processRoutes: Route = pathPrefix("process") {
//    concat(
//      pathPrefix("fibonacci") {
//        concat(
//          path(IntNumber) { n =>
//            pathEnd {
//              concat(
//                get {
//                  val processFuture: Future[ProcessorResponse] = (node ? GetFibonacci(n)).mapTo[ProcessorResponse]
//                  onSuccess(processFuture) { response =>
//                    complete(StatusCodes.OK, response)
//                  }
//                }
//              )
//            }
//          }
//        )
//      }
//    )
//  }
}

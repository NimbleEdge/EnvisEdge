package org.nimbleedge.envisedge.messages

import akka.actor.typed.{ActorRef}
import scala.collection.mutable.{Map => MutableMap}
import org.nimbleedge.envisedge.models._
import org.nimbleedge.envisedge._

final case class SamplingJobSubmit (

    basic_info : JobSubmitBasic,
    trainerList : List[String],
    trainerHistory : MutableMap[String,TrainerHistory]
)
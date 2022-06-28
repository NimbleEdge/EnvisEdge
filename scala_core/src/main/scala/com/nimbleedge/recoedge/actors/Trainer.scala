package com.nimbleedge.recoedge.actors


import akka.actor.{Actor, ActorRef, Props}
import akka.event.Logging
import com.nimbleedge.recoedge.identifiers.TrainerIdentifier
import com.nimbleedge.recoedge.processors.responses.APIObjects._
import com.nimbleedge.recoedge.processors.responses.ProcessorFLManagerResponse
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord}
import spray.json._

import java.util.Properties
import scala.collection.JavaConverters._
import scala.collection.mutable.{Map => MutableMap}
import scala.concurrent.duration._
import scala.util.control.Breaks._


object Trainer {
  // TODO Need to add state
  sealed trait Command

  case class TestTrainerCommand(requestId: String, trainerId: TrainerIdentifier, replyTo: ActorRef) extends Command
  case class TrainerProducerConsumerMessage( requestId :String , message:Message, replyTo :ActorRef ) extends Command

  def props( trainerId: TrainerIdentifier) = Props(new Trainer( trainerId ))

}


class Trainer(trainerId: TrainerIdentifier) extends Actor {

  import Trainer._
  import com.nimbleedge.recoedge.processors.responses.APIObjects.MessageProtocol._

  val log = Logging(context.system, this)

  override def preStart() = {
    log.debug("Starting Trainer")
    log.info("Starting Trainer::info")

  }

  override def receive: Receive = {
    case TestTrainerCommand(value, trainerId , replyTo) =>
      replyTo ! ProcessorFLManagerResponse(value, trainerId.name, "40")

    case  TrainerProducerConsumerMessage( requestId  , message, replyTo ) =>
      log.info( "Inside TrainerProducerConsumerMessage ")
      log.info ( message.toJson.toString() )
      val producerProps:Properties = new Properties()
      producerProps.put("bootstrap.servers","35.154.69.108:9092")
      producerProps.put("key.serializer","org.apache.kafka.common.serialization.StringSerializer")
      producerProps.put("value.serializer","org.apache.kafka.common.serialization.StringSerializer")
      producerProps.put("acks","all")
      val producer = new KafkaProducer[String, String](producerProps)
      try {
        val record = new ProducerRecord[String, String]("nimbleedge-topic", requestId, message.toJson.toString())
        log.info( "Inside TrainerProducerConsumerMessage :: Sending message " + message.toJson.toString() )
        val data = producer.send(record)
      }catch {
        case e: Exception => 
          log.info( "Exception while sending message ")
          e.printStackTrace()
      }
      finally {
        producer.close()
      }
      val consumerProp:Properties = new Properties()
      consumerProp.put("group.id", "console-consumer-89042")
      consumerProp.put("bootstrap.servers","35.154.69.108:9092")
      consumerProp.put("key.deserializer","org.apache.kafka.common.serialization.StringDeserializer")
      consumerProp.put("value.deserializer","org.apache.kafka.common.serialization.StringDeserializer")
      consumerProp.put("enable.auto.commit", "true")
      consumerProp.put("auto.commit.interval.ms", "1000")

      val consumer = new KafkaConsumer[String,String](consumerProp)
      val topics = List("nimbleedge-response-topic")
      try {
        consumer.subscribe(topics.asJava)
        breakable {
          while (true) {
            val records = consumer.poll(10)
            for (record <- records.asScala) {
              if (record.key() == requestId) {
                log.info("Consumer " + record.value())
                break

              }
            }

          }

          



        }

      }catch {
        case e: Exception => e.printStackTrace()
      }
      finally {
        consumer.close()
      }

      replyTo ! ProcessorFLManagerResponse(requestId, message.msg, "40")
  }
}

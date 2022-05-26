package org.nimbleedge.envisedge

import models._
import Utils._

import akka.actor.typed.ActorRef
import akka.actor.typed.Behavior
import akka.actor.typed.scaladsl.Behaviors
import akka.actor.typed.scaladsl.ActorContext
import akka.actor.typed.scaladsl.AbstractBehavior
import akka.actor.typed.Signal
import org.apache.kafka.clients.consumer.{KafkaConsumer,ConsumerRecords, ConsumerRecord}
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord}
import java.time.Duration
import scala.concurrent.Await
import akka.actor.typed.PostStop
import scala.jdk.CollectionConverters._

object TrainerHelper{
    def apply(traId: TrainerIdentifier): Behavior[Command] =
        Behaviors.setup(new TrainerHelper(_, traId))
    
    trait Command

    final case class Consume(topic: String, replyTo: ActorRef[Trainer.Command]) extends Command
    final case class Produce(producer: KafkaProducer[String,String], topic: String, message: String) extends Command
}

class TrainerHelper(context: ActorContext[TrainerHelper.Command], traId: TrainerIdentifier) extends AbstractBehavior[TrainerHelper.Command](context) {
    import TrainerHelper._
    import Trainer.JobResponse

    context.log.info("Trainer Helper {} started", traId.toString())

    override def onMessage(msg: Command): Behavior[Command] =
        msg match {
            case Produce(producer, topic, message) => 
                val result = producer.send(new ProducerRecord(topic, message))
                result.get()
                this

            case Consume(topic, replyTo) => 
                val consumer = new KafkaConsumer[String,String](context.system.settings.config.getConfig("consumer-config").toMap.asJava)
                consumer.subscribe(Vector(topic).asJava)
                val records: ConsumerRecords[String,String] = consumer.poll(Duration.ofSeconds(10))
                val response = if (records.isEmpty()) {
                    "Timeout"
                } else {
                    records.records(topic).iterator().next().value()
                }
                replyTo ! JobResponse(response)
                Behaviors.stopped
        }
    
    override def onSignal: PartialFunction[Signal,Behavior[Command]] = {
        case PostStop =>
            context.log.info("Trainer Helper {} stopped", traId.toString())
            this
    }
}
package org.nimbleedge.envisedge

import akka.actor.testkit.typed.scaladsl.ScalaTestWithActorTestKit
import org.scalatest.wordspec.AnyWordSpecLike
import akka.actor.typed.DispatcherSelector
import java.util.Properties
import org.apache.kafka.clients.consumer.{KafkaConsumer,ConsumerRecords, ConsumerRecord}
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord}
import scala.jdk.CollectionConverters._
import java.time.Duration
import java.util.UUID

class TrainerHelperSpec extends ScalaTestWithActorTestKit with AnyWordSpecLike {
	import models._
    import TrainerHelper._
    import Trainer.JobResponse

    val producerProps = new Properties();
    producerProps.put("bootstrap.servers", "localhost:9092")
    producerProps.put("linger.ms", 1)
    producerProps.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer")
    producerProps.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer")
    producerProps.put("acks", "all")

    val orchId = OrchestratorIdentifier("Orch-1")

    val consumerProps = new Properties();
    consumerProps.put("bootstrap.servers", "localhost:9092")
    consumerProps.put("group.id", UUID.randomUUID().toString())
    consumerProps.put("enable.auto.commit", "true")
    consumerProps.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer")
    consumerProps.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer")
    consumerProps.put("max.poll.records", 1)
    consumerProps.put("auto.offset.reset", "earliest")
    
    // These tests require Kafka server to be running on localhost:9092

	/*"TrainerHelper actor" must {
        "be able to send a message to kafka broker" in {
            val trainerHelper = spawn(TrainerHelper(TrainerIdentifier(orchId,"trainer-1")), DispatcherSelector.blocking())
            val topic = "helper-test-1"
            val message = "Helper Test"
            trainerHelper ! Send(topic,message)
            val consumer = new KafkaConsumer[String,String](consumerProps);
            consumer.subscribe(Vector(topic).asJava);
            val records: ConsumerRecords[String,String] = consumer.poll(Duration.ofSeconds(2));
            records.count() should !== (0)
            records.records(topic).iterator().next().value() should === (message)
            consumer.close()
        }

        "be able to receive a message from kafka broker" in {
            val trainerHelper = spawn(TrainerHelper(TrainerIdentifier(orchId,"trainer-1")), DispatcherSelector.blocking())
            val trainerProbe = createTestProbe[Trainer.Command]()
            val topic = "helper-test-2"
            val message = "Helper Test"
            trainerHelper ! Receive(topic,trainerProbe.ref)
            val producer = new KafkaProducer[String,String](producerProps);
            val result = producer.send(new ProducerRecord(topic, message))
            result.get()
            val response = trainerProbe.receiveMessage()
            response should === (JobResponse(message))
            producer.close()
        }

        "timeout" in {
            val trainerHelper = spawn(TrainerHelper(TrainerIdentifier(orchId,"trainer-1")), DispatcherSelector.blocking())
            val trainerProbe = createTestProbe[Trainer.Command]()
            val topic = "helper-test-3"
            val message = "Helper Test"
            trainerHelper ! Receive(topic,trainerProbe.ref)
            val response = trainerProbe.receiveMessage()
            response should === (JobResponse("Timeout"))
        }
    }*/
}
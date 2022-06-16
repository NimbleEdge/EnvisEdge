package org.nimbleedge.envisedge

import scala.jdk.CollectionConverters._
import com.typesafe.config.Config
import java.util.Properties
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import org.apache.kafka.common.errors.SerializationException
import org.apache.kafka.common.serialization.Serializer
import scala.collection.mutable.{Map => MutableMap}
import com.google.common.hash.Hashing
import java.nio.charset.StandardCharsets

//Circe imports
import io.circe._
import io.circe.parser._

import messages._

import java.io.{StringWriter, PrintWriter}

object Utils {
    implicit class configMapperOps(config: Config) {

    def toMap: Map[String, AnyRef] = config
      .entrySet()
      .asScala
      .map(pair => (pair.getKey, config.getAnyRef(pair.getKey)))
      .toMap
    }
}

object JsonEncoder {
    def serialize(obj: Object) : String = {
      val mapper = new ObjectMapper()
      mapper.registerModule(DefaultScalaModule)    

      val out = new StringWriter
      mapper.writeValue(out, obj)
      val json = out.toString()
      return json
    }
}

object JsonDecoder {
  def deserialize(json_string : String) : Object = {
      val mapper = new ObjectMapper()
      mapper.registerModule(DefaultScalaModule)

      // Parse String Object to check whether it is valid json or not
      json_string.stripMargin
      val parse_result: Either[ParsingFailure,Json] = parse(json_string)

      parse_result match {
          case Left(parsingError) =>
              throw new IllegalArgumentException(s"Invalid json object : ${parsingError.message}")
          case Right(json) =>
                /*val response = mapper.readValue(json_string, classOf[JobResponseMessage])
                println(response)
                return response*/
              // Navigate through the fields of json object
              val cursor: HCursor = json.hcursor
              val job_type : Decoder.Result[String] = 
                  cursor.downField("__type__").as[String]
              
              job_type match {
                  case Left(decodingFailure) => 
                      //throw new IllegalArgumentException(s"Cant find the field : ${decodingFailure}")
                      val response = mapper.readValue(json_string, classOf[MutableMap[String,String]])
                      println(response)
                      return response
                  case Right(__type__) =>
                    val response = mapper.readValue(json_string, classOf[JobResponseMessage])
                    println(response)
                    return response
                      /*if(__type__ == "sampling-response") {
                          println("In Sampling Response")
                          val sampling_response = mapper.readValue(json_string, classOf[Sampling_JobResponse])
                          println(sampling_response)
                          return sampling_response
                      }
                      else if (__type__ == "aggregation-response") {
                          println("In Aggregation Response")
                          val aggregation_response = mapper.readValue(json_string, classOf[Aggregation_JobResponse])
                          println(aggregation_response)
                          return aggregation_response
                      } 
                      // Handle other cases here
                      // Training Response and Recommendation Response
                      else {
                          // If invalid job Type
                          throw new IllegalArgumentException(s"Invalid job_type : ${__type__}")
                      }*/
              }   
      }
  }
}

object Hasher {

  def getHash(data: String): String = {
    return Hashing.md5().hashString(data, StandardCharsets.UTF_8).toString
  }
}

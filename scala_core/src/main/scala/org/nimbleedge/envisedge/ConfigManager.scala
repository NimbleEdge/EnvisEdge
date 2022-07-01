package org.nimbleedge.envisedge

import org.nimbleedge.envisedge.models.OrchestratorIdentifier
import com.typesafe.config.{Config, ConfigFactory}

object ConfigManager {
    val staticConfig = ConfigFactory.load()

    val DEFAULT_TASK_ID = "DEFAULT"
    val AGGR_SAMPLING_REQUEST_TOPIC = "job-request-aggregator"
    val AGGR_SAMPLING_RESPONSE_TOPIC = "job-response-aggregator"
    val AGGR_AGGREGATION_REQUEST_TOPIC = "job-request-aggregator"
    val AGGR_AGGREGATION_RESPONSE_TOPIC = "job-response-aggregator"
    val FLSYS_REQUEST_TOPIC = "fl-system-to-http-service"
    val FLSYS_RESPONSE_TOPIC = "http-service-to-fl-system"
    val NUM_ROUNDS = 5
    val DEFAULT_REDIS_HOST = "localhost"
    val DEFAULT_REDIS_PORT = 6379

    var maxClientsInAgg : Int = 2000
    var minClientsForAggregation: Int = 2
    var samplingPolicy : String = "default"
    var aggregationPolicy: String = "default"

    var aggSamplingConsumerTopics: Vector[String] = Vector(AGGR_AGGREGATION_RESPONSE_TOPIC)
    var aggAggregationConsumerTopics: Vector[String] = Vector(AGGR_SAMPLING_RESPONSE_TOPIC)
    var flSysConsumerTopics: Vector[String] = Vector(FLSYS_RESPONSE_TOPIC)

    var aggregatorS3ProbeIntervalMinutes = 2
    var nextRoundStartIntervalHours = 0.02
    var clientExpireTimeSeconds = 2592000 // 30 days

    def getOrcId(taskId : String) : OrchestratorIdentifier = {
        return OrchestratorIdentifier(taskId)
    }

    def getConsumerTopics(ty: String) : Vector[String] = {
        ty match {
            case "Aggregator" => aggAggregationConsumerTopics ++ aggSamplingConsumerTopics
            case "FLSystemManager" => flSysConsumerTopics
            case _ => throw new IllegalArgumentException(s"Invalid topic type : ${ty}")
        }
    }
}

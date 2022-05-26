name := "EnvisEdge"

version := "0.1"

scalaVersion := "2.13.6"

projectDependencies ++= Seq(
  DefinedDependencies.Akka.actorTyped,
  DefinedDependencies.Logging.slf4jBackend,
  DefinedDependencies.AkkaTest.testkit,
  DefinedDependencies.AkkaTest.scalatest,
  DefinedDependencies.Kafka.kafka
)

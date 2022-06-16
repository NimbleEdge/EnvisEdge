name := "EnvisEdge"

version := "0.1"

scalaVersion := "2.13.6"

projectDependencies ++= Seq(
  DefinedDependencies.Akka.actorTyped,
  DefinedDependencies.Logging.slf4jBackend,
  DefinedDependencies.AkkaTest.testkit,
  DefinedDependencies.AkkaTest.scalatest,
  DefinedDependencies.Kafka.kafka,
  DefinedDependencies.Jackson.jackson_core,
  DefinedDependencies.Jackson.jackson_module,
  DefinedDependencies.Circe.circe_core,
  DefinedDependencies.Circe.circe_generic,
  DefinedDependencies.Circe.circe_parser,
  DefinedDependencies.Redis.client,
  DefinedDependencies.Aws.sdk,
  DefinedDependencies.Aws.conf,
  DefinedDependencies.Guava.guava
)

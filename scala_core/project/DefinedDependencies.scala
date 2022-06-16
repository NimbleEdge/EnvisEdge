import sbt._

object DefinedDependencies {

  private object Versions {
    val akka            = "2.6.19"
    val scalatest       = "3.2.10"
    val logbackClassic  = "1.2.10"
    val kafka           = "3.2.0"
    val jackson_core    = "2.12.1"
    val jackson_module  = "2.12.3"
    val circe           = "0.14.1"
    val redis           = "3.41"
    val aws             = "1.12.230"
    val guava           = "23.0"
  }

  object Akka {
    val actor      = "com.typesafe.akka" %% "akka-actor"       % Versions.akka
    val actorTyped = "com.typesafe.akka" %% "akka-actor-typed" % Versions.akka
    val stream     = "com.typesafe.akka" %% "akka-stream"      % Versions.akka
  }

  object AkkaTest {
    val testkit    = "com.typesafe.akka" %% "akka-actor-testkit-typed" % Versions.akka % Test
    val scalatest  = "org.scalatest" %% "scalatest" % Versions.scalatest % Test
  }

  object Logging {
    val slf4jBackend = "ch.qos.logback" % "logback-classic" % Versions.logbackClassic
  }

  object Kafka {
    val kafka = "org.apache.kafka" % "kafka-clients" % Versions.kafka
  }

  // This library converts scala case class to Json Strings
  object Jackson {
    val jackson_core = "com.fasterxml.jackson.core" % "jackson-databind" % Versions.jackson_core
    val jackson_module = "com.fasterxml.jackson.module" %% "jackson-module-scala" % Versions.jackson_module
  }

  // This library is used to validate whether a given String is in Json format or not
  object Circe {
    val circe_core = "io.circe" %% "circe-core" % Versions.circe
    val circe_generic = "io.circe" %% "circe-generic" % Versions.circe
    val circe_parser = "io.circe" %% "circe-parser" % Versions.circe
  }

  object Redis {
    val client = "net.debasishg" %% "redisclient" % Versions.redis
  }

  object Aws {
    val sdk = "com.amazonaws"	%	"aws-java-sdk" % Versions.aws
    val conf = "com.typesafe" % "config" % "1.4.1" 
  }

  object Guava {
    val guava = "com.google.guava" % "guava" % Versions.guava
  }
}

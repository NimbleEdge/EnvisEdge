import sbt._

object DefinedDependencies {

  private object Versions {
    val akka            = "2.6.18"
    val scalatest       = "3.2.10"
    val logbackClassic = "1.2.10"
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

  object  AmazonS3 {
    val aws = "com.amazonaws"	%	"aws-java-sdk"		%	"1.12.230"
    val typesafeConfig = "com.typesafe" % "config" % "1.4.1"
  }

}

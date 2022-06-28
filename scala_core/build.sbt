name := "akka-cluster"

version := "0.1"

scalaVersion := "2.12.8"

// javacOptions ++= Seq("-source", "1.8", "-target", "1.8", "-Xlint")

// initialize := {
//   val _ = initialize.value
//   val javaVersion = sys.props("java.specification.version")
//   if (javaVersion != "1.8")
//     sys.error("Java 1.8 is required for this project. Found " + javaVersion + " instead")
// }

resolvers ++= Seq(
  "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"
)

lazy val akkaVersion = "2.5.19"
lazy val akkaHttpVersion = "10.1.5"

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-http-spray-json" % akkaHttpVersion,
  "com.typesafe.akka" %% "akka-actor" % akkaVersion,
  "com.typesafe.akka" %% "akka-http" % akkaHttpVersion,
  "com.typesafe.akka" %% "akka-stream" % akkaVersion,
  "com.typesafe.akka" %% "akka-cluster" % akkaVersion,
  "com.typesafe.akka" %% "akka-cluster-tools" % akkaVersion,
  "com.typesafe.akka" %% "akka-stream-kafka" % "1.0.4",
  // "com.lightbend.akka" %% "akka-stream-alpakka-csv" % "1.1.0",
  // "com.lightbend.akka" %% "akka-stream-alpakka-file" % "1.1.0"
)

enablePlugins(JavaAppPackaging)
enablePlugins(DockerPlugin)
enablePlugins(AshScriptPlugin)

mainClass in Compile := Some("com.nimbleedge.recoedge.Server")
dockerBaseImage := "java:8-jre-alpine"
version in Docker := "latest"
dockerExposedPorts := Seq(8000)
dockerRepository := Some("nimbleedge")

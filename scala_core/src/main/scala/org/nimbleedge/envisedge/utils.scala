package org.nimbleedge.envisedge

import scala.jdk.CollectionConverters._
import com.typesafe.config.Config

object Utils {
    implicit class configMapperOps(config: Config) {

    def toMap: Map[String, AnyRef] = config
      .entrySet()
      .asScala
      .map(pair => (pair.getKey, config.getAnyRef(pair.getKey)))
      .toMap
  }
}
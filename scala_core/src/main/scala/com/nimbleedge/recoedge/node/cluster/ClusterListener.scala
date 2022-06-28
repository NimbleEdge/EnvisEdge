package com.nimbleedge.recoedge.node.cluster

import akka.actor.{Actor, ActorLogging, Props}
import akka.cluster.Cluster
import akka.cluster.ClusterEvent._

object ClusterListener {
  def props(nodeId: String, cluster: Cluster) = Props(new ClusterListener(nodeId, cluster))
}

class ClusterListener(nodeId: String, cluster: Cluster) extends Actor with ActorLogging {

  override def preStart(): Unit = {
    cluster.subscribe(self, initialStateMode = InitialStateAsEvents,
      classOf[MemberEvent], classOf[UnreachableMember])
  }

  override def postStop(): Unit = cluster.unsubscribe(self)

  def receive = {
    case MemberUp(member) =>
      log.info("Node {} - Member is Up: {}", nodeId, member.address)
    case UnreachableMember(member) =>
      log.info(s"Node {} - Member detected as unreachable: {}", nodeId, member)
    case MemberRemoved(member, previousStatus) =>
      log.info(s"Node {} - Member is Removed: {} after {}",
        nodeId, member.address, previousStatus)
    case _: MemberEvent => // ignore
  }
}

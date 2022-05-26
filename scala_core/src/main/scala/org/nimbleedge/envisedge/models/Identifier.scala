package org.nimbleedge.envisedge.models

import java.security.{MessageDigest => MD}
import java.nio.ByteBuffer
import scala.collection.mutable.ListBuffer

sealed abstract class Identifier {
  def name(): String
  def computeDigest(): Array[Byte]
  val digest: Array[Byte] = computeDigest()
  override val hashCode: Int = ByteBuffer.wrap(digest.slice(0, 4)).getInt

  def hash(baseName: String, args: List[Identifier]): Array[Byte] = {
    val md = MD.getInstance("SHA-256")
    md.reset()
    md.update(baseName.getBytes("UTF-8"))
    args.foreach(arg => md.update(arg.digest))
    md.digest()
  }

  override def equals(identifier_val: Any): Boolean = {
    identifier_val match {
      case i: Identifier =>
        hashCode == identifier_val.hashCode && MD.isEqual(digest, i.digest)
      case _ => false
    }
  }

  /* Traversal path of the current node from root node.

       For example, if we had a structure like:

       O1
        ├── A1
        │   ├── T1
        │   └── T2
        |
        └── A2
            ├── T3
            ├── T4
            └── A3
                ├── T5
                └── T6

        A2.toList() would return => [O1, A2]
        T5.toList() would return => [O1, A2, A3, T5]
   */
  def toList(): List[Identifier] = List.empty

  // Children
  val children: ListBuffer[Identifier] = ListBuffer.empty
  def getChildren(): List[Identifier] = children.toList

  // TODO
  // The removal of children from the list has to be done manually
}

case class OrchestratorIdentifier(id: String) extends Identifier {
  // String Representation
  override def name(): String = id
  override def toString(): String = id

  // Get List
  override def toList(): List[Identifier] = List(this)

  // Hash digest
  override def computeDigest(): Array[Byte] = hash("_Orc" + id, List.empty)
}

case class AggregatorIdentifier(parentIdentifier: Identifier, id: String) extends Identifier {

  // Add into parents children
  parentIdentifier.children += this

  // String Representation
  override def name(): String = id
  override def toString(): String = parentIdentifier.toString() + " -> " + id

  // Get List
  override def toList(): List[Identifier] =
    parentIdentifier.toList().appended(this)

  // Hash digest
  override def computeDigest(): Array[Byte] =
    hash("_Agg" + id, parentIdentifier.toList())

  // Get Orchestrator
  // Always the root node
  def getOrchestrator(): OrchestratorIdentifier = {
    val orcId = parentIdentifier.toList().head
    orcId match {
      case result @ OrchestratorIdentifier(_) => result
      case _ =>
        throw new IllegalArgumentException(
          "Orchestrator identifier not available."
        )
    }
  }

  // Get List of parent aggregators
  // NOTE: Including the current aggregator identifier
  def getAggregators(): List[AggregatorIdentifier] = {
    parentIdentifier match {
      case OrchestratorIdentifier(_) => List.empty
      case _ =>
        this
          .toList()
          .drop(1)
          .map(value =>
            value match {
              case result @ AggregatorIdentifier(_, _) => result
              case _ =>
                throw new IllegalArgumentException(
                  "Aggregator identifier not available."
                )
            }
          )
    }
  }
}

case class TrainerIdentifier(parentIdentifier: Identifier, id: String) extends Identifier {

  // Add into parents children
  parentIdentifier.children += this

  // String Representation
  override def name(): String = id
  override def toString(): String = parentIdentifier.toString() + " -> " + id

  // Get List
  override def toList(): List[Identifier] =
    parentIdentifier.toList().appended(this)

  // Hash digest
  override def computeDigest(): Array[Byte] =
    hash("_Tra" + id, parentIdentifier.toList())

  // Get Orchestrator
  // Always the root node
  def getOrchestrator(): OrchestratorIdentifier = {
    val orcId = parentIdentifier.toList().head
    orcId match {
      case result @ OrchestratorIdentifier(_) => result
      case _ =>
        throw new IllegalArgumentException(
          "Orchestrator identifier not available."
        )
    }
  }

  // Get List of parent aggregators
  def getAggregators(): List[AggregatorIdentifier] = {
    parentIdentifier match {
      case OrchestratorIdentifier(_) => List.empty
      case _ =>
        parentIdentifier
          .toList()
          .drop(1)
          .map(value =>
            value match {
              case result @ AggregatorIdentifier(_, _) => result
              case _ =>
                throw new IllegalArgumentException(
                  "Aggregator identifier not available."
                )
            }
          )
    }
  }
}

package org.nimbleedge.envisedge.messages

case class AggregatorState (
    worker_index : String,
    round_index : Int,
    state_dict : Map[String, Object],
    storage : String,
    in_neighbours: Map[String, Message],
    out_neighbours: Map[String, Message],
)

case class Neighbour (
    worker_index : String,
    last_sync : Int,
    model_state : Message
)
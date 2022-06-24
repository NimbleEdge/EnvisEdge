package org.nimbleedge.envisedge.messages

import org.nimbleedge.envisedge.Types._

case class AggregatorState (
    worker_id : String,
    round_idx : Int,
    cycle_idx : CycleId,
    state_dict : Map[String, Object],
    storage : String,
    in_neighbours: Map[String, Message],
    out_neighbours: Map[String, Message],
)

case class Neighbour (
    worker_id : String,
    last_sync : Int,
    model_state : Message,
    sample_num: Int
)
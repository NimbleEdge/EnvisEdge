package org.nimbleedge.envisedge.messages

import org.nimbleedge.envisedge.Types._

case class AggregatorState (
    worker_id : String,
    round_idx : Int,
    fl_cycle : CycleId,
    state_dict : Map[String, Object],
    storage : String,
    in_neighbours: Map[String, Message],
    out_neighbours: Map[String, Message],
)

case class Neighbour (
    worker_id : String,
    round_idx : Int,
    fl_cycle : CycleId,
    last_sync : Int,
    state_dict : Map[String, Object],
    sample_num: Int
)
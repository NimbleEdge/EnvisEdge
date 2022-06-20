package org.nimbleedge.envisedge.messages

object JobResponseMessage {
    def deserialize(dict: Map[String, Object]) : JobResponseMessage = {
        return JobResponseMessage (
            job_type = dict("job_type").asInstanceOf[String],
            senderid = dict("senderid").asInstanceOf[String],
            receiverid = dict("receiverid").asInstanceOf[String],
            results = dict("results").asInstanceOf[Map[String,Object]]
        )
    }
}

case class JobResponseMessage (
    job_type : String,
    senderid : String,
    receiverid : String,
    results : Map[String, Object],
)

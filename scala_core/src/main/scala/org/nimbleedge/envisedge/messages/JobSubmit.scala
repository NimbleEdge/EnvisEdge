package org.nimbleedge.envisedge.messages

import javax.annotation.processing.Messager

// This class will contain fields which are common to all type of Job Submit Message

case class JobSubmitMessage (
    job_type : String,
    senderid : String,
    receiverid : String,
    job_args : List[String],
    job_kwargs : List[Object],
    workerstate : Message
)

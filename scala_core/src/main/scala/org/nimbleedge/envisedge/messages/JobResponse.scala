package org.nimbleedge.envisedge.messages

case class JobResponseMessage (
    __type__ : String,
    __data__ : JobResponseData
)

case class JobResponseData (
    job_type : String,
    senderid : String,
    receiverid : String,
    results : String,
)

case class JobResponseResults (
    linearWeight : LinearWeight,
    linearBias : LinearBias
)

case class LinearWeight (
    __type__ : String,
    __data__ : Storage
)

case class LinearBias (
    __type__ : String,
    __data__ : Storage
)

case class Storage (
    storage : String,
)






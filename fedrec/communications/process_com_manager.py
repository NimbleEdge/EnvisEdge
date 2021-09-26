
from fedrec.utilities import registry
from fedrec.communications.messages import JobResponseMessage
from fedrec.communications.comm_manager import (CommunicationManager,
                                                tag_reciever)


@registry.load("process_comm_manager", "zeroMQ_process_comm_manager")
class ProcessComManager(CommunicationManager):
    def __init__(self, config_dict):
        super().__init__(config_dict=config_dict)

    def run(self):
        super().run()

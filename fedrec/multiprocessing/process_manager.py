import mpi4py
from fedrec.communications.process_com_manager import ProcessComManager
from fedrec.utilities import registry
from fedrec.multiprocessing.job import Jobber
from mpi4py import MPI
import asyncio
class MPIProcessManager:

    def __init__(self, config) -> None:
        self.pool = MPI.COMM_WORLD
        self.rank = self.pool.Get_rank()
        self.num_processes = self.pool.Get_size()
        if self.rank !=0:
            self.jobber = Jobber(trainer = registry.lookup("trainer"), logger = registry.lookup("logger"))
            self.enqueued_jobs = asyncio.Queue(maxsize=config["max_jobs_per_process"])
            self.process_comm_manager = ProcessComManager(config_dict=config["comm_manager_config"])
            self.loop = asyncio.get_event_loop()



    def run(self) -> None:
        if self.rank != 0:
            self.loop.create_task(self.consume())
            self.loop.create_task(self.run_jobs())
            self.loop.run_forever()

    async def consume(self) -> None:
        while True:
            if not self.enqueued_jobs.full():
                job_request = self.process_comm_manager.handle_receive_message()
                if job_request is not None:
                    if job_request.JOB_TYPE == "STOP":
                        # Runs current batch of callbacks and then exit
                        self.loop.stop()
                        return
                    await self.enqueued_jobs.put(job_request)


    async def run_jobs(self) -> None:
        while True:
            job_request = await self.enqueued_jobs.get()
            job = self.loop.create_task(self.jobber.run(job_request))
            job.add_done_callback(self.publish())



    def publish(self, job_result) -> None:
        self.enqueued_jobs.task_done()
        self.process_comm_manager.send_message(job_result.result())
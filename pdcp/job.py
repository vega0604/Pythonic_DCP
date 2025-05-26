from pdcp import dcp
from pdcp.custom_types import JobConfig, ComputeGroup, EventHandler


class Job:
    '''
    Description:
        A class that represents a `Job` object.

    Attributes:
        job_config -> `JobConfig`: configuration of the job
    '''
    def __init__(self, job_config: JobConfig):
        self.config = job_config

        self.name = self.config["name"]

        work_function = self.config["work_function"]
        constant_params = self.config.get("constant_params", [])
        slices = self.config.get("slices", [])
        self.input_count = len(slices)
        
        self.job = dcp.compute_for(slices, work_function, constant_params)
        self.compute_groups = self.config.get("compute_groups", [])
        self.job.autoClose = not self.config.get("stream_slices", False)

        self.results = []

        self.subscribe_to({
            "result": lambda e: self.results.append(e.result)
        })

        self.chains: list[Job] = []

    def add_slices(self, slices: list):
        if self.job.autoClose == False:
            dcp.job.addSlices(slices, self.id)
        else:
            raise Exception("Job is not configured to stream slices")

    def subscribe_to(self, events: EventHandler):
        for event, callback in events.items():
            self.job.on(event, callback)

    @property
    def id(self):
        return self.job.id
    
    @property
    def compute_groups(self):
        return self.job.computeGroups
    
    @compute_groups.setter
    def compute_groups(self, compute_groups: list[ComputeGroup]):
        self.job.computeGroups = compute_groups
    
    def dispatch(self):
        self.job.exec()

    def get_results(self):
        self.job.wait() # TODO: This is a hack to wait for the job to finish
        return self.results
    
    def chain(self, config: JobConfig):
        # TODO: This is a surface level implementation of chaining jobs
        job = Job(config)
        self.chains.append(job)
        return job
    
if __name__ == "__main__":
    def work(x: int, a: int) -> int:
        dcp.progress()
        return x * a
        
    config: JobConfig = {
        "name": "test",
        "work_function": work,
        "slices": [1, 2, 3],
        "constant_params": [3],
        "compute_groups": [{"joinKey": "sheridan", "joinSecret": "dcp"}]
    }
    job = Job(config)
    job.subscribe_to({
        "readystatechange": print,
        "accepted": lambda _: print(f'accepted: {job.id}'),
        "result": lambda e: print(f'result: {e.result}'),
        "status": lambda e: print(f'status: {e.runStatus}')
    })

    job.dispatch()
    results = job.get_results()
    print(results)

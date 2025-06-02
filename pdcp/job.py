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
        self.expected_output_count = len(slices)
        
        self.job = dcp.compute_for(slices, work_function, constant_params)
        self.compute_groups = self.config.get("compute_groups", [])
        self.job.autoClose = not self.config.get("stream_slices", False)

        self.results = []

        self.chained_configs: list[JobConfig] = []
        self.chained_jobs: list[Job] = []

        self.interceptor: callable | None = None

        self.event_subscriptions: EventHandler | None = self.config.get('event_subscriptions', None)
        if self.event_subscriptions:
            self.subscribe_to(self.event_subscriptions)

    def add_slices(self, slices: list):
        if self.job.autoClose == False:
            dcp.job.addSlices(slices, self.id)
        else:
            raise Exception("Job is not configured to stream slices")

    def subscribe_to(self, events: EventHandler):
        self.event_subscriptions = events
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

    def disperse_outputs(self, event):
        self.results.append(event.result)
        for job in self.chained_jobs:
            job.add_slices(event.result)

        if len(self.results) == self.expected_output_count:
            self.job.close()
            
    def dispatch(self):
        if self.config.get("stream_slices", False):
            self.subscribe_to({
                "result": self.disperse_outputs
            })
            for config in self.chained_configs:
                config["stream_slices"] = True
                job = Job(config)
                self.chained_jobs.append(job)
                job.dispatch()

            self.job.exec()
        else:
            self.job.exec()
            self.results = self.job.wait()
            for config in self.chained_configs:
                config["slices"] = self.results
                job = Job(config)
                self.chained_jobs.append(job)
                job.dispatch()

    def get_results(self):
        return self.results
    
    def chain(self, config: JobConfig):
        # TODO: This is a surface level implementation of chaining jobs
        # TODO: We need to make this a lot more robust
        self.chained_configs.append(config)
        return self
    
if __name__ == "__main__":
    def work(x: int, a: int) -> int:
        dcp.progress()
        return x * a
    
    def work2(x: int):
        dcp.progress()
        return f"processed: {x} again"
        
    config: JobConfig = {
        "name": "test",
        "work_function": work,
        "slices": [1, 2, 3],
        "expected_output_count": 3,
        "constant_params": [3],
        "compute_groups": [{"joinKey": "sheridan", "joinSecret": "dcp"}]
    }

    config2: JobConfig = {
        'name': "chained",
        'work_function': work2,
        'expected_output_count': 3,
        'compute_groups': [{"joinKey": "sheridan", "joinSecret": "dcp"}],
        'event_subscriptions': {
            'accepted': print,
            'readystatechange': print,
            'result': lambda e: print(e.result)
        }
    }

    job = Job(config)
    job.subscribe_to({
        "readystatechange": print,
        "accepted": lambda _: print(f'accepted: {job.id}'),
        "result": lambda e: print(f'result: {e.result}'),
        "status": lambda e: print(f'status: {e.runStatus}')
    })

    job.chain(config2)

    job.dispatch()
    results = job.get_results()
    chain_results = [j.get_results() for j in job.chained_jobs]
    print(results)
    print(chain_results)

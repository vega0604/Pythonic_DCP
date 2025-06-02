from pdcp import dcp
from pdcp.custom_types import JobConfig, JobResult, EventHandler
from rich import print_json

class Job:
    '''
    Description:
        A class that represents a `Job` object.

    Attributes:
        job_config -> `JobConfig`: configuration of the job
    '''
    # TODO: CHANGE TO JUST CONFIG, JOB CREATION ON DISPATCH
    def __init__(self, job_config: JobConfig):
        self.config = job_config
        self.job = self.create_job()

        self.chained_configs: list[JobConfig] = []
        self.chained_jobs: list[Job] = []

        self.interceptor: callable | None = None

        self.results: JobResult = {"name": self.config["name"], "results": [], "chains": []}

        self.subscribe_to(self.config.get('event_subscriptions', {}))

    # def add_slices(self, slices: list):
    #     if self.job.autoClose == False:
    #         dcp.job.addSlices(slices, self.id)
    #     else:
    #         raise Exception("Job is not configured to stream slices")

    def subscribe_to(self, events: EventHandler):
        if self.job is None:
            raise Exception("Job is unitialized")
        for event, callback in events.items():
            self.job.on(event, callback)

    @property
    def id(self):
        return self.job.id

    # def disperse_outputs(self, event):
    #     self.results.append(event.result)
    #     for job in self.chained_jobs:
    #         job.add_slices(event.result)

    #     if len(self.results) == self.expected_output_count:
    #         self.job.close()

    def create_job(self):
        work_function = self.config['work_function']
        constant_params = self.config.get("constant_params", [])
        slices = self.config.get("slices", [])

        job = dcp.compute_for(slices, work_function, constant_params)
        job.computeGroups = self.config.get('compute_groups', [])
        job.autoClose = not self.config.get("stream_slices", False)
        return job

    def dispatch(self):
        # if self.config.get("stream_slices", False):
        #     self.subscribe_to({
        #         "result": self.disperse_outputs
        #     })
        #     for config in self.chained_configs:
        #         config["stream_slices"] = True
        #         job = Job(config)
        #         self.chained_jobs.append(job)
        #         job.dispatch()

        #     self.job.exec()
        # else:
        self.job.exec()
        job_results = self.job.wait()
        self.results["results"].extend(job_results)
        
        for config in self.chained_configs:
            config["slices"] = job_results
            job = Job(config)
            chain_results = job.dispatch()
            self.results["chains"].append(chain_results)

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
        "compute_groups": [{"joinKey": "sheridan", "joinSecret": "dcp"}],
        "event_subscriptions": {
            "readystatechange": print,
            "accepted": lambda _: print(f'accepted: {job.id}'),
            "result": lambda e: print(f'result: {e.result}'),
            "status": lambda e: print(f'status: {e.runStatus}')
        }
    }

    config2: JobConfig = {
        'name': "chained",
        'work_function': work2,
        'expected_output_count': 3,
        'compute_groups': [{"joinKey": "sheridan", "joinSecret": "dcp"}],
        'event_subscriptions': {
            'readystatechange': print,
            'accepted': print,
            'result': lambda e: print(e.result)
        }
    }

    job = Job(config)

    job.chain(config2)
    job.chain(config)

    results = job.dispatch()
    print_json(data=results)

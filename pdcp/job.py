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
    # TODO: ADD INTERCEPTOR LOGIC
    def __init__(self, job_config: JobConfig):
        self.config = job_config
        self.job = None

        self.chained_jobs: list[Job] = []

        self.interceptor: callable | None = None

        self.results: JobResult = {"name": self.config["name"], "results": [], "chains": []}

    # def add_slices(self, slices: list):
    #     if self.job.autoClose == False:
    #         dcp.job.addSlices(slices, self.id)
    #     else:
    #         raise Exception("Job is not configured to stream slices")

    def set_slices(self, slices: list):
        self.config["slices"] = slices

    def subscribe_to(self, events: EventHandler):
        if self.job is None:
            raise Exception("Job is unitialized")
        for event, callback in events.items():
            self.job.on(event, callback)

    @property
    def id(self):
        if self.job is None:
            raise Exception("Job is unitialized")
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
        #     return self.streamed_dispatch()
        self.job = self.create_job()
        self.subscribe_to(self.config.get('event_subscriptions', {}))
        self.job.exec()

        job_results = self.job.wait()
        self.results["results"].extend(job_results)
        
        for chained_job in self.chained_jobs:
            chained_job.set_slices(job_results)
            chain_results = chained_job.dispatch()
            self.results["chains"].append(chain_results)

        return self.results
    
    def chain(self, config: JobConfig):
        job = Job(config)
        self.chained_jobs.append(job)
        return job
    
if __name__ == "__main__":
    def work(x: int, a: int) -> int:
        dcp.progress()
        return x * a
    
    def work2(x: int, a: int):
        dcp.progress()
        return x // a
        
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
        'constant_params': [3],
        'compute_groups': [{"joinKey": "sheridan", "joinSecret": "dcp"}],
        'event_subscriptions': {
            'readystatechange': print,
            'accepted': print,
            'result': lambda e: print(e.result)
        }
    }

    job = Job(config)

    job.chain(config2).chain(config)
    job.chain(config2).chain(config2)

    results = job.dispatch()
    print_json(data=results)

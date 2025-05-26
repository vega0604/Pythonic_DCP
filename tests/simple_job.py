from pdcp import Job
from pdcp.custom_types import JobConfig
from pdcp.utils import work_function

if __name__ == "__main__":
    @work_function
    def work(x: int, a: int) -> int:
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
from pdcp import Job, dcp
from pdcp.custom_types import JobConfig
from rich import print_json

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
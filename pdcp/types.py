from typing import TypedDict, NotRequired

class ComputeGroup(TypedDict):
    joinKey: str
    joinSecret: str

class EventHandler(TypedDict):
    readystatechange: NotRequired[callable]
    accepted: NotRequired[callable]
    result: NotRequired[callable]
    complete: NotRequired[callable]
    console: NotRequired[callable]
    status: NotRequired[callable]

class JobConfig(TypedDict):
    '''
    Description:
        A TypedDict that describes the configuration of a `Job` object.

    Attributes:
        work_function -> `callable`: function to be executed
        stream_slices -> `bool`: equivalent to the opposite of `dcp.job.Job.autoClose`
        constant_params -> `NotRequired[list[any]]`: list of constant parameters for the work function
        compute_groups -> `NotRequired[list[ComputeGroup]]`: list of compute groups
    '''
    name: str
    work_function: callable
    slices: NotRequired[list]
    stream_slices: NotRequired[bool]
    constant_params: NotRequired[list[any]]
    compute_groups: NotRequired[list[ComputeGroup]]
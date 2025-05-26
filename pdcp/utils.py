
def work_function(func):
    '''
    Description:
        A decorator that handles dcp progress updates. CURRENTLY NOT USED

    Args:
        func -> `callable`: the function to be wrapped

    Returns:
        A wrapped function that updates the progress of the job.
    '''
    def wrapper(*args, **kwargs):
        import dcp
        dcp.progress()
        result = func(*args, **kwargs)
        return result
    return wrapper

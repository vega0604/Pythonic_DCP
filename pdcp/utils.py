from functools import wraps

def work_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import dcp
        dcp.progress()
        result = func(*args, **kwargs)
        return result
    return wrapper

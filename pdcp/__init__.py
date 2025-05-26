'''
PDCP is a Pythonic wrapper for the DCP (Distributed Computing Protocol) API.
'''
import dcp
from .job import Job
from . import custom_types
from . import utils
dcp.init()

__all__ = ['Job', 'custom_types', 'utils', 'dcp']

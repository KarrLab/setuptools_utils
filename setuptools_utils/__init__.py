from .core import *
import pkg_resources

# read version
with open(pkg_resources.resource_filename('setuptools_utils', 'VERSION'), 'r') as file:
    __version__ = file.read().strip()
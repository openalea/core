#import importlib.metadata

#__version__ =  importlib.metadata.version("openalea.core")

#numbers = __version__.split(".")

"""
try:
    major, minor, post = numbers[0], numbers[1], numbers[2]
    patch = '.'.join(numbers[3:])
except IndexError:
    major, minor, post = '2', '4', '3'
    patch = '0'
    __version__ = '.'.join([major, minor, post])
"""

major, minor, post = '2', '4', '3'
patch = 'a1'
__version__ = '.'.join([major, minor, post, patch])

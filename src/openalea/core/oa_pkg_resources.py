"""
This module is a module compatibility between pkg_resources that is deprecated and the use of alternative
that are importlib_resources, importlib_metadata
`here <url>`__https://setuptools.pypa.io/en/latest/pkg_resources.html
    Use of pkg_resources is deprecated in favor of importlib.resources, importlib.metadata and their backports
    (importlib_resources, importlib_metadata). Some useful APIs are also provided by packaging
    (e.g. requirements and version parsing). Users should refrain from new usage of pkg_resources and should work
    to port to importlib-based solutions.
"""
import sys
import pathlib
from importlib.metadata import entry_points, distributions, PathDistribution

class Wrapper_distribution:
    def __init__(self,dist,location,egg_name = None):
        self._dist = dist
        self.location = location

    def __getattr__(self, item):
        return getattr(self._dist, item)

    def egg_name(self):
        name = self._dist.metadata['Name'].replace('-', '_')  # normalize like setuptools
        version = self._dist.version
        py_tag = f"py{sys.version_info.major}.{sys.version_info.minor}"
        return f"{name}-{version}-{py_tag}"

class ExtendedEntryPoint:
    def __init__(self, entry_point, module_name, dist=None):
        self._entry_point = entry_point
        self.module_name = module_name
        self.dist = dist or self._find_dist()

    def __getattr__(self, item):
        return getattr(self._entry_point, item)

    def _find_dist(self):
        # Find and return a wrapped distribution with .location
        for dist in distributions():
            if self._entry_point in dist.entry_points:
                location = dist.locate_file('')
                return Wrapper_distribution(dist, location)
        return None  # Not found

    def load(self):
        return self._entry_point.load()
class Distrib:
    def __init__(self,dist):
        self._dist = dist
        self.project_name = dist.name

    # def __getattr__(self, item):
    #     return getattr(self._dist, item)

    def get_entry_map(self):
        entry_map = {}
        for ep in self._dist.entry_points:
            entry_map.setdefault(ep.group, []).append(ep)
        return entry_map

def find_distributions(path):
    path = pathlib.Path(path)
    for dist_info in path.glob('*.dist-info'):
        try:
            _dist = PathDistribution(dist_info)
            yield Distrib(_dist)

        except Exception as e:
            print(f"Error reading {dist_info.name}: {e}")

def iter_entry_points(group: str, name: str | None = None):
    eps = entry_points(group=group)
    # Wrap each entry point in ExtendedEntryPoint
    my_eps = [ExtendedEntryPoint(ep, ep.module) for ep in eps]
    return my_eps

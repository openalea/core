from __future__ import absolute_import
from __future__ import print_function

import openalea.core

from openalea.core.pkgmanager import PackageManager

from .small_tools import test_dir

def oa_dir():
    return openalea.core.__path__[0]

# test has been removed
# adding OS directories ensure fail of pm.init()
# since pkgmanager is a singleton, other tests
# evaluated in parallel failed too

# def test_wraleapath():
#     """test wraleapath"""
#     pkgman = PackageManager()
#
#     # this option (include_namespace has been removed)
#     #    assert bool(openalea.__path__[0] in  \
#     #      pkgman.get_wralea_path()) == pkgman.include_namespace
#
#     if (os.name == 'posix'):
#         pkgman.add_wralea_path("/usr/bin", pkgman.user_wralea_path)
#         assert "/usr/bin" in pkgman.get_wralea_path()
#     else:
#         pkgman.add_wralea_path("C:\\Windows", pkgman.user_wralea_path)
#         assert "C:\\Windows" in pkgman.get_wralea_path()


def test_load_pm():
    pkgman = PackageManager()
    pkgman.load_directory(oa_dir())

    simpleop = pkgman["openalea.flow control"]
    assert simpleop

    addfactory = simpleop.get_factory('command')
    assert addfactory != None
    assert addfactory.instantiate()

    valfactory = simpleop.get_factory('rendez vous')
    assert valfactory != None


def test_category():
    pkgman = PackageManager()
    pkgman.load_directory(oa_dir())

    #pkgman.init()
    #pkgman.find_and_register_packages()

    # test if factory are dedoubled
    for cat in pkgman.category.values():
        s = set()
        for factory in cat:
            assert not factory in s
            s.add(factory)


def test_search():
    pkgman = PackageManager()
    pkgman.load_directory(test_dir())

    assert 'Test' in pkgman

    res = pkgman.search_node("sum")
    print(res)
    assert "sum" in res[0].name.lower()


    # comment these 3 lines because system.command is not part
    # of any nodes anymore.
    # res = pkgman.search_node("system.command")
    # print res
    # assert "command" in res[0].name

# test has been removed
# too dangerous to test writing on a singleton
# while other test may be modifying the config

# def test_write_config():
#     pkgman = PackageManager()
#     pkgman.load_directory("./")
#     pkgman.write_config()
#     p = pkgman.user_wralea_path
#
#     s = Settings()
#     path = s.get("pkgmanager", "path")
#     paths = list(eval(path))  # path is a string
#
#     assert set(paths) == set(p)

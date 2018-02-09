from os.path import exists
from os.path import join as pj

from openalea.core.package import *
from openalea.core.node import gen_port_list

from .small_tools import ensure_created, rmdir


def test_package():
    metainfo = {'version': '0.0.1',
                'license': 'CECILL-C',
                'authors': 'OpenAlea Consortium',
                'institutes': 'INRIA/CIRAD',
                'description': 'Base library.',
                'url': 'http://openalea.gforge.inria.fr',
                'icon': ''}

    package = Package("Test", metainfo)
    assert package is not None


class TestUserPackage():
    def setUp(self):
        self.tmp_dir = "toto_test_package"
        ensure_created(self.tmp_dir)
        ensure_created(pj(self.tmp_dir, "tstpkg"))

    def tearDown(self):
        rmdir("toto_test_package")

    def test_case_1(self):
        metainfo = {'version': '0.0.1',
                    'license': 'CECILL-C',
                    'authors': 'OpenAlea Consortium',
                    'institutes': 'INRIA/CIRAD',
                    'description': 'Base library.',
                    'url': 'http://openalea.gforge.inria.fr',
                    'icon': ''}

        path = pj(self.tmp_dir, "tstpkg")
        mypackage = UserPackage("DummyPkg", metainfo, path)

        factory = mypackage.create_user_node("TestFact",
                                             "category test",
                                             "this is a test",
                                             gen_port_list(3),
                                             gen_port_list(2))
        assert path in factory.search_path
        assert len(factory.inputs) == 3
        assert len(factory.outputs) == 2

        assert exists(pj(path, "TestFact.py"))
        execfile(pj(path, "TestFact.py"))

        mypackage.write()
        assert exists(pj(path, "__wralea__.py"))
        assert exists(pj(path, "__init__.py"))
        execfile(pj(path, "__wralea__.py"))

        # Test_clone_package
        path = pj(self.tmp_dir, "clonepkg")
        pkg2 = UserPackage("ClonePkg", metainfo, path)
        print pkg2.wralea_path

        # todo this is not working !!
        # from openalea.core.pkgmanager import PackageManager
        # pm = PackageManager()
        # pm.add_wralea_path(path, pm.temporary_wralea_paths)
        # pm.init()
        # pkg2.clone_from_package(mypackage)
        # pkg2.write()
        #
        # assert len(pkg2) == 1
        # assert len(pkg2["TestFact"].inputs) == 3
        # assert id(pkg2["TestFact"]) != id(mypackage["TestFact"])
        # assert exists(path)
        # assert exists(pj(path, '__wralea__.py'))
        # assert exists(pj(path, '__init__.py'))
        # assert exists(pj(path, 'TestFact.py'))

from __future__ import absolute_import
import os

from openalea.core.config import Config

class MyModelUnit:
    def __init__(self, name, params={}):
        self.name = name

    
def test_config1():


    unit1 = MyModelUnit('unit1', dict(p1=1, p2='2'))
    unit2 = MyModelUnit('unit2', dict(p1=1, p2='2'))

    config = Config([unit1, unit2])
    config.dump('toto.yml')

    assert(len(config) == 2)
    assert(len(config['unit1'])==2)


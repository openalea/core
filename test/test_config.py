from __future__ import absolute_import
import os

from openalea.core.config import Config

import yaml
import json

class Parameter:
    def __init__(self, name, value=None, unit=None, param_type=None, description="", uid=None, uri=None):
        self.name =  name
        self.value = value
        self.unit = unit
        self.param_type = param_type
        self.description = description
        self.uid = uid
        self.uri = uri

    def to_dict(self):
        return {
            "name":self.name,
            "value": self.value,
            "unit": self.unit,
            "param_type": self.param_type,
            "description": self.description,
            "uid": self.uid,
            "uri": self.uri
        }

class MyModelUnit:
    def __init__(self, name, parameters: dict):
        self.name = name
        self.parameters=parameters

    def to_dict(self):
        return {
            self.name : self.parameters
        }

    def __str__(self):
        return f"name={self.name}, parameters={self.parameters}"

    
def test_config1():

    unit1 = MyModelUnit('unit1', dict(p1=1, p2='2'))
    unit2 = MyModelUnit('unit2', dict(p1=1, p2='2'))

    p1= Parameter("numerical", 12, "cm", "cm", "mesurer", 234, 1223)

    unit3=MyModelUnit('unit3', p1.to_dict())
    print(unit3)

    config1 = Config(unit3.to_dict())
    print(config1)
    config1.dump("tototo.json")
    
    #config1 = Config([unit1, unit2])
    #config1.dump("toto.json")  
    config2 = Config.load(unit1, "toto.json")
    
    '''
    assert(len(config) == 2)
    assert(len(config['unit1'])==2)
    '''

test_config1()




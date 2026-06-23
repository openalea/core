# -*- python -*-
#
#       OpenAlea.Core
#
#       Copyright 2006-2026 CIRAD - INRAE - inria
#
#       File author(s): Leticia Napolitano
#                       Christophe Pradal <christophe.prada@cirad.fr>
#                       Fabrice Bauget <fabrice.bauget@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
##############################################################################
"""Configuration of OpenAlea models"""

__license__ = "Cecill-C"

import yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import json
from openalea.core.singleton import Singleton
from openalea.core.observer import Observed
from pathlib import Path
from dataclasses import dataclass, asdict
import io
from ruamel.yaml import YAML

def _load_json(filename: str):
    """Load configuration from a JSON file."""
    
    file = Path(filename)
    with file.open() as f:
        data = json.load(f)
    return data

def _load_yml(filename: str):
    """Load configuration from a YAML file."""

    file = Path(filename)
    with file.open() as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def _dump_yml(data, filename: str, sort_keys=False):
    """Dump configuration to a YAML file."""

    file = Path(filename)
    with file.open("w") as f:
        yaml.dump(data, f, sort_keys=sort_keys)

def _dump_json(data, filename: str):
    """Dump configuration to a JSON file."""
    
    file = Path(filename)
    with file.open("w") as f:
        json.dump(data, f, indent=4)

def to_commented_map(obj):
    if isinstance(obj, dict):
        cm = CommentedMap()
        for k, v in obj.items():
            cm[k] = to_commented_map(v)
        return cm
    else:
        return obj


def add_comment(cm):
  
    for name, param in cm["simulation"].items():
        for key, value in param.items():
            param.yaml_set_comment_before_after_key(
                key,
                before=f"{key}: {value}"
            )


@dataclass 
class Parameter:
    name: str
    value: any = None
    unit: str = None
    param_type: str = None
    description: str = ""
    uid: str = None
    uri: str = None

    def __to_dict__(self):
        d = asdict(self)
        name = d.pop("name")
        return {name: d}
    
    def __str__(self):
        return (
            f"name={self.name}, value={self.value}, unit={self.unit}, "
            f"param_type={self.param_type}, description={self.description}, "
            f"uid={self.uid}, uri={self.uri}"
        )


class ModelUnit(dict):
    def __init__(self, name, parameters: list):
    
        params_dict = {}
        for p in parameters:
            params_dict.update(p.__to_dict__())

        super().__init__({name: params_dict})
        self.name = name
        self.parameters=parameters

    def __str__(self):
        return f"name={self.name}, parameters={dict(self)}"


class Config(dict):
    """Configuration of OpenAlea models
    
    TODO : Documentation to write
    """

    def __init__(self, model_unit_configs: list):
        """Initialize the configuration with a list of unit configurations."""

        super().__init__()
        self.model_unit_configs = model_unit_configs
        for unit in model_unit_configs:
            self.update(unit)

    def __len__(self):
        return len(self.model_unit_configs)


    def __str__(self):
        return f"{self.model_unit_configs}"

    def add_section(self, unit):
        self.model_unit_configs.append(unit)
        self.update(unit)

    #@staticmethod
    def load(self, filename: str):
        """Load configuration from a file.
        
        Dispatch method based on file extension (YAML, JSON, etc.).
        """

        extension = filename.split(".")[-1]

        if extension in ("yml", "yaml"):
            data = _load_yml(filename)

        elif extension == "json":
            data = _load_json(filename)

        units = []

        '''
        for unit_name, params in data.items():
            parameters = [Parameter(name=k, value=v) for k, v in params.items()]
            unit = MyModelUnit(unit_name, parameters)
            units.append(unit)
        '''
        for unit_name, params in data.items():
            parameters = [
            Parameter(
            name=name,
            value=params[name]["value"],
            unit=params[name].get("unit"),
            description=params[name].get("description"),
            param_type=params[name].get("type"),
            uid=params[name].get("uid"),
            uri=params[name].get("uri")
        )
            for name in params
    ]

            units.append(ModelUnit(unit_name, parameters))

        return Config(units)

    def dump(self, filename: str):
        """Dump configuration to a file."""

        extension = filename.split(".")[-1]

        #add_comment(self)

        if extension in ("yml", "yaml"):
            yaml = YAML()
            cm = to_commented_map(self)
            add_comment(cm)

            with open(filename, "w") as f:
                yaml.dump(cm, f)
                #_dump_yml(dict(self), filename)

        elif extension == "json":
            _dump_json(dict(self), filename)



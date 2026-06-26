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

def add_comment2(cm, model_unit_configs):
    
    param_index = {}
    for unit in model_unit_configs:
        param_index[unit.name] = {}
        for p in unit.parameters:
            param_index[unit.name][p.name] = p

    for section_name, section in cm.items():
        for param_name in section:
            param = param_index.get(section_name, {}).get(param_name)
            fields = ["description", "unit", "param_type", "uid", "uri"]
            comments = []
            if param:
                for field in fields:
                    value = getattr(param, field)
                    if value is not None:
                        comments.append(f"{field}: {value}")
            if comments:
                section.yaml_set_comment_before_after_key(
                    param_name,
                    before="\n".join(comments)
                )


def add_comment(cm, custom_comments=None):
    if custom_comments is None:
        custom_comments = {}

    for section_name, section in cm.items():
        for param_name, param_value in section.items():
            if param_name in custom_comments:
                comment = custom_comments[param_name]

                if isinstance(comment, list):
                    comment = "\n".join(comment)

                section.yaml_set_comment_before_after_key(
                    param_name,
                    before=comment
                )


def add_section_comments(cm, section_comments):
    for section_name in cm.keys():
        if section_name in section_comments:
            comment = section_comments[section_name]

            if isinstance(comment, list):
                comment = "\n".join(comment)

            cm.yaml_set_comment_before_after_key(
                section_name,
                before=comment
            )

@dataclass 
class Parameter:
    name: str
    value: any = None
    description : any = None
    unit : any = None
    param_type : any = None
    uid : any = None
    uri : any = None


    def __to_dict__(self):
        return {self.name: self.value}
    
    def __str__(self):
        return (
            f"name={self.name}, value={self.value}"
        )

'''
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
'''

class ModelUnit(dict):
    def __init__(self, name, parameters: list):
        super().__init__({name: {p.name: p.value for p in parameters}})
        self.name = name
        self.parameters = parameters

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
        self.params_comments = {}
        self.section_comments = {}

        for unit in model_unit_configs:
            self.update(unit)

    def __len__(self):
        return len(self.model_unit_configs)


    def __str__(self):
        return f"{self.model_unit_configs}"

    def add_section(self, unit):
        self.model_unit_configs.append(unit)
        self.update(unit)


    def load(self, filename: str):
        extension = filename.split(".")[-1]

        if extension in ("yml", "yaml"):
            yaml = YAML()
            with open(filename, "r") as f:
                data = yaml.load(f)

        elif extension == "json":
            data = _load_json(filename)

        units = []

        for unit_name, params in data.items():
            parameters = []
            for param_name, param_value in params.items():
                p = Parameter(name=param_name, value=param_value)
                parameters.append(p)

            units.append(ModelUnit(unit_name, parameters))

        return Config(units)


    def dump(self, filename: str):
        """Dump configuration to a file."""

        extension = filename.split(".")[-1]

        if extension in ("yml", "yaml"):
            yaml = YAML()
            cm = to_commented_map(self)
            

            add_comment(cm, self.params_comments)
            add_comment2(cm, self.model_unit_configs)
            add_section_comments(cm, self.section_comments)


            with open(filename, "w") as f:
                yaml.dump(cm, f)

        elif extension == "json":
            _dump_json(dict(self), filename)



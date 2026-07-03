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
    """
    Load a configuration from a JSON file.
    :param filename: the JSON configuration file.
    """
    
    file = Path(filename)
    with file.open() as f:
        data = json.load(f)
    return data

def _load_yml(filename: str):
    """
    Load a configuration from a YAML file.
    :param filename: the YAML configuration file.
    """

    file = Path(filename)
    with file.open() as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def _dump_yml(data, filename: str, sort_keys=False):
    """
    Dump configuration to a YAML file.
    :param data: configuration data to write.
    :param filename: YAML file path.
    :param sort_keys: sort keys.
    """

    file = Path(filename)
    with file.open("w") as f:
        yaml.dump(data, f, sort_keys=sort_keys)

def _dump_json(data, filename: str):
    """
    Dump configuration to a JSON file.
    :param data: configuration data to write.
    :param filename: JSON file path.
    """
    
    file = Path(filename)
    with file.open("w") as f:
        json.dump(data, f, indent=4)

def to_commented_map(obj):
    """
    Convert a Python dictionary into a ruamel.yaml CommentedMap.
    :param obj: dictionary.
    """

    if isinstance(obj, dict):
        cm = CommentedMap()
        for k, v in obj.items():
            cm[k] = to_commented_map(v)
        return cm
    else:
        return obj

def add_unit_comment(cm, model_unit_configs):
    """
    Add comments above each ModelUnit section.
    The comments are generated from optional ModelUnit fields: description, unit, param_type, uid, and uri.
    :param cm: CommentedMap.
    :param model_unit_configs: List of ModelUnit objects.
    """

    fields = ["description", "unit", "param_type", "uid", "uri"]

    for unit in model_unit_configs:
        comments = []

        for field in fields:
            value = getattr(unit, field, None)
            if value is not None:
                comments.append(f"{field}: {value}")

        if comments:
            cm.yaml_set_comment_before_after_key(
                unit.name,
                before="\n".join(comments)
            )


def add_comment2(cm, model_unit_configs):
    """
    Add comments to each parameter. Comments are generated from optional Parameter fields: 
    description, unit, param_type, uid, and uri.
    If the value is None, this function doesn't add a new comment. If the value is not None, we add the comment.   
    :param cm: CommentedMap.
    :param model_unit_configs: List of ModelUnit objects.          
    """
    
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


@dataclass 
class Parameter:
    """
    Represent a configuration parameter.
    The dataclass Parameter has two mandatory parameters name and value. The others parameters are optional to the configuration, if
    we add them this would be commented.
    The parameter can be converted to dictionary.
    """
    name: str
    value: any 
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


class ModelUnit(dict):
    """
    Represent a configuration sectiion with a name a list of parameters.
    :param name: Name of the section.
    :param parameters: List of Parameter objects.
    :param description: Optional description of the section.
    """
    def __init__(self, name, parameters: list, description=None, unit=None, param_type=None, uid=None, uri=None):
        super().__init__({name: {p.name: p.value for p in parameters}})
        self.name = name
        self.parameters = parameters
        self.description = description
        self.uid = uid
        self.uri = uri

    def __str__(self):
        return f"name={self.name}, parameters={dict(self)}"


class Config(dict):
    """
    Configuration of OpenAlea models.
    A Config object is a dictionary that contains a list of ModelUnit. A config can load, dump, add new sections, new sections,
    the quantity of units.
    :param model_unit_configs: List of ModelUnit objects.
    """

    def __init__(self, model_unit_configs: list):
        """
        Initialize the configuration with a list of unit configurations.
        """

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
        """
        Load a configuration file (YAML or JSON) and return a new Config.
        :param filename: configuration file.
        """

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
        """
        Dump the configuration to a YAML or JSON file.
        :param filename: filename path.
        """

        extension = filename.split(".")[-1]

        if extension in ("yml", "yaml"):
            yaml = YAML()
            cm = to_commented_map(self)
            
            add_comment2(cm, self.model_unit_configs)
            add_unit_comment(cm, self.model_unit_configs)

            with open(filename, "w") as f:
                yaml.dump(cm, f)

        elif extension == "json":
            _dump_json(dict(self), filename)

    def get_sections(self):
        """
        Return the list of section names in the configuration.
        """

        return list(self.keys())

    def get_parameters(self, section_name):
        """
        Return the list of parameter names of a section.
        :param section_name: Name of the section.
        """

        if section_name not in self:
            raise KeyError(f"Section '{section_name}' doesn't exist.")
        return list(self[section_name].keys())



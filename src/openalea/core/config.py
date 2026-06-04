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
import json
from openalea.core.singleton import Singleton
from openalea.core.observer import Observed
from pathlib import Path

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

def _dump_yml(data, filename: str):
    """Dump configuration to a YAML file."""
    
    file = Path(filename)
    with file.open("w") as f:
        yaml.dump(data, f)

def _dump_json(data, filename: str):
    """Dump configuration to a JSON file."""
    
    file = Path(filename)
    with file.open("w") as f:
        json.dump(data, f)


class Config:
    """Configuration of OpenAlea models
    
    TODO : Documentation to write
    """
    def __init__(self, model_unit_configs: dict):
        """Initialize the configuration with a list of unit configurations."""
        self.model_unit_configs = model_unit_configs

    def __str__(self):
        return f"{self.model_unit_configs}"

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

        print(data)

        return Config(data)

    def dump(self, filename: str):
        """Dump configuration to a file."""

        extension = filename.split(".")[-1]

        if extension in ("yml", "yaml"):
            _dump_yml(self.model_unit_configs, filename)

        elif extension == "json":
            _dump_json(self.model_unit_configs, filename)

   

    
#   update()
#   to_dict()
#   build_model() --create a model object
#   generate()

# class ModelUnitConfig
#   [Parameters]
#   name
#   uid
#   uri
#   description
#   validate() --validation des sections
#   to_dict()

# class Parameter
#   name
#   value
#   unit
#   type
#   description
#   default value
#   uid
#   uri

# class ModelConfig
#   [ModelUnitConfig]
#   name
#   def MyModel()
#      p = params() --recover parameters
#      c = Config(p)
#      c.generate('config.yml')
#   return Model(c)
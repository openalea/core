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


from openalea.core.singleton import Singleton
from openalea.core.observer import Observed

class Config:
    """Configuration of OpenAlea models
    
    TODO : Documentation to write
    """
    def __init__(self, model_unit_configs):
        """Initialize the configuration with a list of unit configurations."""
        self.model_unit_configs = model_unit_configs

    @staticmethod
    def load(self, filename: str):
        """Load configuration from a file.
        
        Dispatch method based on file extension (YAML, JSON, etc.).
        """
        return Config()

    def dump(self, filename: str):
        """Dump configuration to a file."""

    def _load_yml(self, filename: str):
        """Load configuration from a YAML file."""

    def _dump_yml(self, filename: str):
        """Dump configuration to a YAML file."""

    def _load_json(self, filename: str):
        """Load configuration from a JSON file."""

    def _dump_json(self, filename: str):
        """Dump configuration to a JSON file."""

    
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
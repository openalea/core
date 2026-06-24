from __future__ import absolute_import
import os
from openalea.core.config import Parameter, ModelUnit, Config
import yaml
import json

def hydroshoot_simulation_config():

    p_sdate = Parameter("sdate", "2012-08-01 00:00:00")
    print("t")
    print(p_sdate)
    p_edate = Parameter("edate", "2012-08-04 23:00:00")
    p_lat = Parameter("latitude", 43.61)
    p_longitude = Parameter("longitude", 3.87)
    p_elevation = Parameter("elevation", 44.0)
    p_tzone = Parameter("tzone", "Europe/Paris")
    p_output_index = Parameter("output_index", "")
    p_unit_scene_length = Parameter("unit_scene_length", "cm")
    p_hydraulic_structure = Parameter("hydraulic_structure", True)
    p_negligible_shoot_resistance = Parameter("negligible_shoot_resistance", False)
    p_energy_budget = Parameter("energy_budget", True)
    parameters = [p_sdate, p_edate, p_lat, p_longitude, p_elevation, p_tzone, p_output_index, p_unit_scene_length, p_hydraulic_structure, p_negligible_shoot_resistance, p_energy_budget]
    simulation = ModelUnit('simulation', parameters)
    print(simulation)

    return simulation

def hydroshoot_planting_config():
    p_spacing_between_rows = Parameter("spacing_between_rows", 3.6)
    p_spacing_on_row = Parameter("spacing_on_row", 1)
    p_row_angle_with_south = Parameter("row_angle_with_south", 140.0)

    parameters = [p_spacing_between_rows, p_spacing_on_row, p_row_angle_with_south]
    planting = ModelUnit('planting', parameters)

    return planting

def hydroshoot_phenology_config():
    p_emdate = Parameter("emdate", "2012-04-01 00:00:00")
    p_t_base = Parameter("t_base", 10.0)

    parameters = [p_emdate, p_t_base]
    phenology = ModelUnit('phenology', parameters)

    return phenology

def test_config_hs():
    unit = hydroshoot_simulation_config()
    config = Config([unit])
    config.dump("params4.yml")
    
    assert(len(config) == 1)
    assert(len(config['simulation'])==11)
    
    planting = hydroshoot_planting_config()
    config.add_section(planting)
    config.dump("params4.yml")

    assert len(config) == 2
    assert len(config["planting"]) == 3

    phenology = hydroshoot_phenology_config()
    config.add_section(phenology)
    config.custom_comments["sdate"] = "date of simulation"
    config.custom_comments["latitude"] = [
    "param_type : float",
    "unit : degrees"
]
    config.dump("params4.yml")

    config.load("params4.yml")

    assert len(config) == 3
    assert len(config["planting"]) == 3
    

test_config_hs()




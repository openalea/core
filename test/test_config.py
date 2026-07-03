from openalea.core.config import Parameter, ModelUnit, Config
import yaml
import json

def hydroshoot_simulation_config():

    p_sdate = Parameter("sdate", "2012-08-01 00:00:00", "Start date of the simulation", None, "datetime")
    p_edate = Parameter("edate", "2012-08-04 23:00:00", "End date of the simulation", None, "datetime")
    p_lat = Parameter("latitude", 43.61, None, "degrees", "float")
    p_longitude = Parameter("longitude", 3.87, "Longitude of the simulation", "degrees", "float")
    p_elevation = Parameter("elevation", 44.0, "Elevation of the simulation", "meters", "float")
    p_tzone = Parameter("tzone", "Europe/Paris", "Time zone", None, "string")
    p_output_index = Parameter("output_index", "", "Output index", None, "string")
    p_unit_scene_length = Parameter("unit_scene_length", "cm", "Unit of scene length", None, "string")
    p_hydraulic_structure = Parameter("hydraulic_structure", True, "Hydraulic structure", None, "boolean")
    p_negligible_shoot_resistance = Parameter("negligible_shoot_resistance", False, "Negligible short resistance", None, "boolean")
    p_energy_budget = Parameter("energy_budget", True, "Energy budget", None, "boolean")
    parameters = [p_sdate, p_edate, p_lat, p_longitude, p_elevation, p_tzone, p_output_index, p_unit_scene_length, p_hydraulic_structure, p_negligible_shoot_resistance, p_energy_budget]
    simulation = ModelUnit("simulation", parameters, "Simulations parameters")
    
    print(simulation)

    return simulation

def hydroshoot_planting_config():
    p_spacing_between_rows = Parameter("spacing_between_rows", 3.6, "Distance between planting rows", "meters", "float")
    p_spacing_on_row = Parameter("spacing_on_row", 1, "Spacing on the row", "meters", "float")
    p_row_angle_with_south = Parameter("row_angle_with_south", 140.0, "Row angle with south", "degrees", "float")

    parameters = [p_spacing_between_rows, p_spacing_on_row, p_row_angle_with_south]
    planting = ModelUnit('planting', parameters, "Planting section")

    return planting

def hydroshoot_phenology_config():
    p_emdate = Parameter("emdate", "2012-04-01 00:00:00", "Emergence date", None, "datetime")
    p_t_base = Parameter("t_base", 10.0, "Base temperature", "degrees", "float")

    parameters = [p_emdate, p_t_base]
    phenology = ModelUnit('phenology', parameters, "Phenology section")

    return phenology

def hydroshoot_mtg_api_config():
    p_collar_label = Parameter("collar_label", "inT", "Collar label", None, "string")
    p_leaf_lbl_prefix = Parameter("leaf_lbl_prefix", "L", "Leaf label prefix", None, "string")
    p_stem_lbl_prefix = Parameter("stem_lbl_prefix", ["in", "Pet", "cx"], "Stem label prefix", None, "list")

    parameters = [p_collar_label, p_leaf_lbl_prefix, p_stem_lbl_prefix]
    mtg_api = ModelUnit("mtg_api", parameters, "Mtg api section")

    return mtg_api

def hydroshoot_numerical_resolution_config():
    p_max_iter = Parameter("max_iter", 100, "Maximum number of iterations", None, "integer")
    p_psi_step = Parameter("psi_step", 1.0, "Psi step", None, "float")
    p_psi_error_threshold = Parameter("psi_error_threshold", 0.05, "Psi error threshold", "seconds")
    p_t_step = Parameter("t_step", 1.0, "Time step", None, "float")
    p_t_error_threshold = Parameter("t_error_threshold", 0.02, "Time error threshold", "float")

    parameters = [p_max_iter, p_psi_step, p_psi_error_threshold, p_t_step, p_t_error_threshold]
    numerical_resolution = ModelUnit("numerical_resolution", parameters, "Numerical section")

    return numerical_resolution


def test_config_hs():
    unit = hydroshoot_simulation_config()
    config = Config([unit])
    config.dump("params4.yml")
    
    assert(len(config) == 1)
    assert(len(config['simulation'])==11)
    config.section_comments["simulation"] = "Simulation"
    planting = hydroshoot_planting_config()
    config.add_section(planting)
    config.dump("params.yml")

    assert len(config) == 2
    assert len(config["planting"]) == 3

    phenology = hydroshoot_phenology_config()
    config.add_section(phenology)
    mtg_api = hydroshoot_mtg_api_config()
    config.add_section(mtg_api)
    config.dump("params.yml")

    numerical_resolution = hydroshoot_numerical_resolution_config()
    config.add_section(numerical_resolution)
    config.dump("params.yml")
    config.dump("params.json")

    config.load("params.yml")

    assert len(config) == 5
    assert len(config["planting"]) == 3
    value = config["simulation"]["sdate"]
    print('value ' + value)
    section = config["simulation"]
    print('section')
    print(section)
    

test_config_hs()




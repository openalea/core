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
            self.name:self.value
        }

    def __str__(self):
        return f"name={self.name}, value={self.value}, unit={self.unit}, param_type={self.param_type}, description={self.description}, uid={self.uid}, uri={self.uri}"

class MyModelUnit:
    def __init__(self, name, parameters: list):
        self.name = name
        self.parameters=parameters
    
    def to_dict(self):
        params = {k : v  for param in self.parameters for k, v in param.to_dict().items()}
        return {
            self.name : params
        }
    

    def __str__(self):
        return f"name={self.name}, parameters={self.to_dict()}"

def hydroshoot_simulation_config():

    p_sdate = Parameter("sdate", "2012-08-01 00:00:00")
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

    simulation = MyModelUnit('simulation', parameters)
    return simulation

def test_config_hs_simu():
    unit = hydroshoot_simulation_config()
    config = Config([unit])

    # tests
    assert(len(config) == 1)
    assert(len(config['simulation'])==11)


def test_config1():

    #unit1 = MyModelUnit('unit1', dict(p1=1, p2='2'))
    #unit2 = MyModelUnit('unit2', dict(p1=1, p2='2'))

    #p1= Parameter("numerical", 12, "cm", "cm", "mesurer", 234, 1223)

    #unit3=MyModelUnit('unit3', p1.to_dict())
    #print(unit3)

    #config1 = Config(unit3.to_dict())
    #print(config1)
    #config1.dump("tototo.json")
    
    #config1 = Config([unit1, unit2])
    #config1.dump("toto.json")  
    #config2 = Config.load(unit1, "toto.json")

    '''TEST WITH JSON'''

    print("Test  params.json of HydroShoot\n")

    # Creation of the simulation section



    
    

    unit_simulation = hydroshoot_simulation_config()

    # Creation of the planting section

    p_spacing_between_rows = Parameter("spacing_between_rows", 3.6)
    p_spacing_on_row = Parameter("spacing_on_row", 1)
    p_row_angle_with_south = Parameter("row_angle_with_south", 140.0)
    parameters2 = [p_spacing_between_rows, p_spacing_on_row, p_row_angle_with_south]

    
    unit_planting_section = MyModelUnit('planting', parameters2)

    #Creation of the phenology section

    p_emdate = Parameter("emdate", "2012-04-01 00:00:00")
    p_t_base = Parameter("t_base", 10.0)

    p3 = [p_emdate, p_t_base]
    d3 = {}
    d3.update(p_emdate.to_dict())
    d3.update(p_t_base.to_dict())

    unit_phenology = MyModelUnit("phenology", p3)

    # Creation of the MTG API section 
    
    p_collar_label = Parameter("collar_label", "inT")
    p_leaf_lbl_prefix = Parameter("leaf_lbl_prefix", "L")
    p_stem_lbl_prefix = Parameter("stem_lbl_prefix", ["in", "Pet", "cx"])

    p4 = [p_collar_label, p_leaf_lbl_prefix, p_stem_lbl_prefix]
    d4 = {}
    d4.update(p_collar_label.to_dict())
    d4.update(p_leaf_lbl_prefix.to_dict())
    d4.update(p_stem_lbl_prefix.to_dict())

    #


    unit_mtg_api = MyModelUnit("mtg_api", d4)

    #Creation of the numerical resolution section

    p_max_iter = Parameter("max_iter", 100)
    p_psi_step = Parameter("psi_step", 1.0)
    p_psi_error_threshold = Parameter("psi_error_threshold", 0.05)
    p_t_step = Parameter("t_step", 1.0)
    p_t_error_threshold = Parameter("t_error_threshold", 0.02)

    d5 = {}
    d5.update(p_max_iter.to_dict())
    d5.update(p_psi_step.to_dict())
    d5.update(p_psi_error_threshold.to_dict())
    d5.update(p_t_step.to_dict())
    d5.update(p_t_error_threshold.to_dict())

    unit_numerical_resolution = MyModelUnit("numerical_resolution", d5)

    #Creation of the irradiance section

    p_E_type = Parameter("E_type", "Rg_Watt/m2")
    p_E_type2 = Parameter("E_type2", "Eabs")

    p_opt_prop = Parameter("opt_prop", {
        "SW": {
            "leaf": [0.06, 0.07],
            "stem": [0.13],
            "other": [0.06, 0.07]
        },
        "LW": {
            "leaf": [0.04, 0.07],
            "stem": [0.13],
            "other": [0.06, 0.07]
        }
    })

    p_turtle_format = Parameter("turtle_format", "soc")
    p_turtle_sectors = Parameter("turtle_sectors", "46")
    p_icosphere_level = Parameter("icosphere_level", None)

    d6 = {}
    d6.update(p_E_type.to_dict())
    d6.update(p_E_type2.to_dict())
    d6.update(p_opt_prop.to_dict())
    d6.update(p_turtle_format.to_dict())
    d6.update(p_turtle_sectors.to_dict())
    d6.update(p_icosphere_level.to_dict())

    unit_irradiance = MyModelUnit("irradiance", d6)

    #Creation of the energy section

    
    p_solo = Parameter("solo", True)
    p_t_cloud = Parameter("t_cloud", 2.0)
    p_t_sky = Parameter("t_sky", -20.0)

    d7 = {}
    d7.update(p_solo.to_dict())
    d7.update(p_t_cloud.to_dict())
    d7.update(p_t_sky.to_dict())

    unit_energy = MyModelUnit("energy", d7)

    #Creation of the hydraulic section

    p_psi_min = Parameter("psi_min", -3.0)

    p_Kx_dict = Parameter("Kx_dict", {
        "a": 1.6,
        "b": 2.0,
        "min_kmax": 0.000111
    })

    p_par_K_vul = Parameter("par_K_vul", {
        "model": "misson",
        "fifty_cent": -0.76,
        "sig_slope": 1.0
    })

    d8 = {}
    d8.update(p_psi_min.to_dict())
    d8.update(p_Kx_dict.to_dict())
    d8.update(p_par_K_vul.to_dict())

    unit_hydraulic = MyModelUnit("hydraulic", d8)

    #Creation of the exchange section

    p_rbt = Parameter("rbt", 0.6667)

    p_Na_dict = Parameter("Na_dict", {
        "aN": -0.0008,
        "bN": 3.3,
        "aM": 6.471,
        "bM": 56.635
    })

    p_par_gs = Parameter("par_gs", {
        "model": "misson",
        "g0": 0.0,
        "m0": 7.3,
        "psi0": -0.65,
        "D0": 1.0,
        "n": 4.0
    })

    p_par_photo = Parameter("par_photo", {
        "alpha": 0.24,
        "Kc25": 404.9,
        "Ko25": 278.4,
        "Tx25": 42.75,
        "ds": 0.635,
        "dHd": 200.0,
        "RespT_Kc": {"c": 38.05, "deltaHa": 79.43},
        "RespT_Ko": {"c": 20.30, "deltaHa": 36.38},
        "RespT_Vcm": {"c": 26.35, "deltaHa": 65.33},
        "RespT_Jm": {"c": 17.57, "deltaHa": 43.54},
        "RespT_TPU": {"c": 21.46, "deltaHa": 53.1},
        "RespT_Rd": {"c": 18.72, "deltaHa": 46.39},
        "RespT_Tx": {"c": 19.02, "deltaHa": 37.83}
    })

    p_par_photo_N = Parameter("par_photo_N", {
        "Vcm25_N": [34.02, -3.13],
        "Jm25_N": [78.27, -17.3],
        "Rd_N": [0.42, -0.01],
        "TPU25_N": [6.24, -1.92]
    })

    d9 = {}
    d9.update(p_rbt.to_dict())
    d9.update(p_Na_dict.to_dict())
    d9.update(p_par_gs.to_dict())
    d9.update(p_par_photo.to_dict())
    d9.update(p_par_photo_N.to_dict())

    unit_exchange = MyModelUnit("exchange", d9)

    #Creation of the soil section

    p_soil_class = Parameter("soil_class", "Sandy_Loam")

    p_soil_dimensions = Parameter("soil_dimensions", {
        "width": 3.6,
        "length": 1.0,
        "depth": 1.2
    })

    p_rhyzo_coeff = Parameter("rhyzo_coeff", 0.75)

    d10 = {}
    d10.update(p_soil_class.to_dict())
    d10.update(p_soil_dimensions.to_dict())
    d10.update(p_rhyzo_coeff.to_dict())

    unit_soil = MyModelUnit("soil", d10)


    #Configuration

    config_dict = {}

    config_dict.update(unit_simulation.to_dict())
    config_dict.update(unit_planting_section.to_dict())
    config_dict.update(unit_phenology.to_dict())
    config_dict.update(unit_mtg_api.to_dict())
    config_dict.update(unit_numerical_resolution.to_dict())
    config_dict.update(unit_irradiance.to_dict())
    config_dict.update(unit_energy.to_dict())
    config_dict.update(unit_hydraulic.to_dict())
    config_dict.update(unit_exchange.to_dict())
    config_dict.update(unit_soil.to_dict())


    config3 = Config(config_dict)
    print(config3)
    config3.dump("params.json")

    '''TEST WITH YML'''

    config4 = Config(config_dict)
    config4.dump("params.yml")

    # Creation of the simulation section

    p_sdate1 = Parameter("sdate", "2012-08-01 00:00:00")
    p_edate1 = Parameter("edate", "2012-08-04 23:00:00")
    p_lat1 = Parameter("latitude", 43.61)
    p_longitude1 = Parameter("longitude", 3.87)
    p_elevation1 = Parameter("elevation", 44.0)

    d11 = {}
    d11.update(p_sdate.to_dict())
    d11.update(p_edate.to_dict())
    d11.update(p_lat.to_dict())
    d11.update(p_longitude.to_dict())
    d11.update(p_elevation.to_dict())
    
    unit_simulation1 = MyModelUnit('simulation', d11)

    # Creation of the planting section

    p_spacing_between_rows1 = Parameter("spacing_between_rows", 3.6)
    p_spacing_on_row1 = Parameter("spacing_on_row", 1)
    p_row_angle_with_south1 = Parameter("row_angle_with_south", 140.0)

    d12={}
    d12.update(p_spacing_between_rows.to_dict())
    d12.update(p_spacing_on_row.to_dict())
    d12.update(p_row_angle_with_south.to_dict())

    unit_planting_section1 = MyModelUnit('planting', d12)

     #Configuration

    config_dict1 = {}

    config_dict1.update(unit_simulation1.to_dict())
    config_dict1.update(unit_planting_section1.to_dict())

    config5 = Config(config_dict1)
    config5.dump("paramss.yml")

    '''
    assert(len(config) == 2)
    assert(len(config['unit1'])==2)
    '''

def test_read_cnofig():
    config = load_config("params.json")
    config.dump("params1.json")
    # compare both
    print(config)




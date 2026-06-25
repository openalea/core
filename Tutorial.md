# Tutorial of the configuration 

This tutorial explains how the configuration work on the model. User, modeler and developer interact with the configuration. The user update the file, the modeler build the file and the developer use config to init the model and run it.

## User

The user interacts only with the configuration file, not with Python code.
The user can modify the YAML and JSON file. He can change the values, the parameters and also comment.
The file can be opened with a text editor or on Visual Studio Code. 
The configuration file is written in YAML or JSON and contains sections, parameters inside each section.

For example, in HydroRoot with simulation and planting as sections with their parameters: 
simulation:
  sdate: '2012-08-01 00:00:00'
  edate: '2012-08-04 23:00:00'
  latitude: 43.61
  longitude: 3.87
  elevation: 44.0
  tzone: Europe/Paris
  output_index: ''
  unit_scene_length: cm
  hydraulic_structure: true
  negligible_shoot_resistance: false
  energy_budget: true
planting:
  spacing_between_rows: 3.6
  spacing_on_row: 1
  row_angle_with_south: 140.0

The user can modify only the values, never the parameter names but can never change the name of parameters. He can change latitude 43.61 to 41 for example. The user can also comment, comments begin with #. JSON doesn't support comment, if the user want to comment, he have to use YAML.

## Modeler

The modeler constructs the configuration. A Config is a Python dictionary that stores sections and parameters. A Config is built from a list of ModelUnit objects.

For example:
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
simulation = ModelUnit('simulation', parameters)
config = Config([simulation])

The modeler can also load and dump a configuration file as config.dump("params.yml") or config.dump("params.json"). The modeler can also add new sections, for example *config.add_section(planting)*.

## Developer

The developer receives a config object. Config unherite from a dict, the developer can access to the parameters value. He can initialize the model and call run().
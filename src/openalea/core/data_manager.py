import dill
import os
from openalea.core.metadata.cloud_info import CACHE_PATH, TMP_PATH
from openalea.distributed.index.id import get_id

def write_data(data_id, data, path):
    """
    vid: vid of the node whose output will be stored
    path: path where the data will be stored
    """
    with open(os.path.join(path,data_id), "w") as f:
        dill.dump(data, f)


# def write_outputs(data_id, cache_path):
#     for port in range(df.node(vid).get_nb_output()):
#         data_id = get_id(vid, port)
#         with open(os.path.join(cache_path,data_id), "w") as f:
#             dill.dump(df.node(vid).get_output(port), f)


def load_data(path):
    """
    vid: vid of the node whose input will be fetched
    path: path of the data to get
    """
    with open(path, "r") as f:
        data = dill.load(f)
    return data


def check_data_to_load(vid, pid, fragment_infos):
    """
    Return the path if the data has to be loaded 
    Return None otherwise

    """
    if not fragment_infos:
        return None
    if (vid, pid) in fragment_infos['cached_data'].keys():
        # the data is get from cache 
        return fragment_infos['cached_data'][(vid, pid)]
    if (vid, pid) in fragment_infos['input_data'].keys():
        # the data is computed by other fragments
        return fragment_infos['input_data'][(vid, pid)]
    return None


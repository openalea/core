import dill
import os


def write_data(vid, path):
    """
    vid: vid of the node whose output will be stored
    path: path where the data will be stored
    """

    return
def write_outputs(df, vid, cache_path):
    for port in range(df.node(vid).get_nb_output()):
        data_id = str(vid) + "_" + str(port)
        with open(os.path.join(cache_path,data_id), "w") as f:
            dill.dump(df.node(vid).get_output(port), f)

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
    if (vid, pid) in fragment_infos['input_data'].keys():
        # the data is computed by other fragments
        return fragment_infos['input_data'][(vid, pid)]
    if (vid, pid) in fragment_infos['cached_data'].keys():
        # the data is get from cache 
        return fragment_infos['cached_data'][(vid, pid)]
    return None
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
PARAM_FILE = os.path.join(THIS_DIR, "../scenario_setup/parameters.json")
PY_MAKE_TOPOLOGY = os.path.join(THIS_DIR, "../scenario_setup")

sys.path.append(PY_MAKE_TOPOLOGY)
from make_topology import make_small_world_topology


def read_parameters():
    with open(PARAM_FILE, "r") as f:
        configs = json.load(f)

    return (configs["n_runs"], configs["simulation_configs"])


def get_topology(config):
    n = config["number_of_agents"]
    k = config["small_world_k"]
    p = config["small_world_p"]
    seed = config["rng_seed"]
    return make_small_world_topology(n, k, p, seed)

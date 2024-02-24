import asyncio
import math
import time
import os
import datetime
import csv
import pandas as pd

from sim_agent import SimAgent, PingMessage, PongMessage, AgentAddress
from mango import create_container
from mango.messages.codecs import JSON

from input_parser import read_parameters, get_topology

CONTAINER_PORT_BASE = 5555
HOST = "localhost"

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
RESULT_DIR = os.path.join(THIS_DIR, "../results")


async def make_agents_and_containers(
    adjacenccy_matrix, agent_lists, config, periodic_processes, instant_processes
):
    containers = []
    agents = []
    n_containers = len(agent_lists)

    codec = JSON()
    codec.add_serializer(*PingMessage.__serializer__())
    codec.add_serializer(*PongMessage.__serializer__())

    for i in range(n_containers):
        c = await create_container(addr=(HOST, CONTAINER_PORT_BASE + i), codec=codec)
        containers.append(c)

    for container_id, agent_list in enumerate(agent_lists):
        for aid in agent_list:
            agent = SimAgent(
                containers[container_id],
                config["work_on_message_in_seconds"],
                config["work_periodic_in_seconds"],
                config["n_periodic_tasks"],
                config["delay_periodic_in_seconds"],
                config["message_amount"],
                config["message_size_bytes"],
                config["message_nesting_depths"],
                f"{aid}",
                periodic_processes,
                instant_processes,
            )

            agents.append(agent)

    # set neighborhoods
    for aid, agent in enumerate(agents):
        neighbors = []
        n_ids = adjacenccy_matrix[aid]
        for n_id, value in enumerate(n_ids):
            if value == 1:
                neighbors.append(agents[n_id])

        neighbor_addresses = [
            AgentAddress(n.addr[0], n.addr[1], n.aid) for n in neighbors
        ]

        agent.set_neighbors(neighbor_addresses)

    return (agents, containers)


def container_to_agents(config):
    n_agents = config["number_of_agents"]
    n_containers = config["number_of_containers"]
    agents_per_container = math.ceil(n_agents / n_containers)
    output = []

    for _ in range(n_containers):
        output.append([])

    for i in range(n_agents):
        # 0:agents_per_container-1 map to container 0
        # agents_per_container:2*agents_per_container-1 map to container 1
        # ...
        container_id = i // agents_per_container
        output[container_id].append(i)

    return output


async def run_simulation(config, periodic_processes, instant_processes):
    adjacency_matrix = get_topology(config)
    agent_lists = container_to_agents(config)
    agents, containers = await make_agents_and_containers(
        adjacency_matrix, agent_lists, config, periodic_processes, instant_processes
    )

    start_time = time.time()

    await asyncio.gather(*[a.run_agent() for a in agents])
    await asyncio.gather(*[c.shutdown() for c in containers])

    time_elapsed = time.time() - start_time

    print(time_elapsed)

    return time_elapsed


def save_sim_results(results, file_prefix):
    if not os.path.isdir(RESULT_DIR):
        os.mkdir(RESULT_DIR)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
    filename = file_prefix + timestamp + ".csv"
    output_file = os.path.join(RESULT_DIR, filename)

    df = pd.DataFrame(results)
    df.to_csv(output_file)


async def main():
    # await c.shutdown()
    n_runs, configs = read_parameters()
    results = {}

    # Vanilla python mango
    periodic_processes = instant_processes = False

    for config in configs:
        result_times = [0] * n_runs

        for i in range(n_runs):
            result_times[i] = await run_simulation(
                config, periodic_processes, instant_processes
            )

        results[config["simulation_name"]] = result_times

    save_sim_results(results, "python_single_process_")

    # process periodics
    periodic_processes = True
    instant_processes = False

    for config in configs:
        result_times = [0] * n_runs

        for i in range(n_runs):
            result_times[i] = await run_simulation(
                config, periodic_processes, instant_processes
            )

        results[config["simulation_name"]] = result_times

    save_sim_results(results, "python_periodic_processes_")

    # process both
    periodic_processes = instant_processes = True

    for config in configs:
        result_times = [0] * n_runs
        for i in range(n_runs):
            result_times[i] = await run_simulation(
                config, periodic_processes, instant_processes
            )

        results[config["simulation_name"]] = result_times

    save_sim_results(results, "python_all_processes_")


if __name__ == "__main__":
    asyncio.run(main())

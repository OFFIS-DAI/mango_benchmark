import asyncio
import math
import time
import os
import datetime
import pandas as pd

from sim_agent import SimAgent, PingMessage, PongMessage, AgentAddress
from mango import create_container
from mango.messages.codecs import JSON
from multiprocessing import Event

from input_parser import read_parameters, get_topology

CONTAINER_PORT_BASE = 5555
HOST = "localhost"

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
RESULT_DIR = os.path.join(THIS_DIR, "../results")


def aid_to_container_id(aid, config):
    n_agents = config["number_of_agents"]
    n_containers = config["number_of_containers"]
    agents_per_container = math.ceil(n_agents / n_containers)

    return aid // agents_per_container


async def make_agents_and_containers(
    adjacenccy_matrix,
    agent_lists,
    config,
    periodic_processes,
    instant_processes,
    agent_processes,
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
            if agent_processes:
                event = Event()
                event.clear()

                def agent_creator_sub_process(c):
                    agent = SimAgent(
                        c,
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
                        mp_event=event,
                    )
                    set_neighbors_to_agent(
                        adjacenccy_matrix, config, containers, aid, agent
                    )

                p_handle = containers[container_id].as_agent_process(
                    agent_creator=agent_creator_sub_process
                )
                agents.append((containers[container_id], p_handle.pid, event))
                await p_handle

            else:
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
                set_neighbors_to_agent(
                    adjacenccy_matrix, config, containers, aid, agent
                )

                agents.append(agent)

    return (agents, containers)


def set_neighbors_to_agent(adjacenccy_matrix, config, containers, aid, agent):
    neighbors = []
    n_ids = adjacenccy_matrix[aid]
    for n_id, value in enumerate(n_ids):
        if value == 1:
            neighbors.append(n_id)

    neighbor_addresses = [
        AgentAddress(
            containers[aid_to_container_id(n, config)].addr[0],
            containers[aid_to_container_id(n, config)].addr[1],
            f"{n}",
        )
        for n in neighbors
    ]
    agent.set_neighbors(neighbor_addresses)


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


async def call_run_pid(container):
    for _, agent in container._agents.items():
        await agent.run_agent()
        agent.mp_event.set()


async def wait_for_processes_to_run(container_to_pid):
    events = []
    for container, pid, event in container_to_pid:
        container.dispatch_to_agent_process(pid, call_run_pid)
        events.append(event)
    for event in events:
        while not event.is_set():
            await asyncio.sleep(0.05)


async def run_simulation(
    config, periodic_processes, instant_processes, agent_processes
):
    adjacency_matrix = get_topology(config)
    agent_lists = container_to_agents(config)
    agents, containers = await make_agents_and_containers(
        adjacency_matrix,
        agent_lists,
        config,
        periodic_processes,
        instant_processes,
        agent_processes,
    )

    start_time = time.time()

    if agent_processes:
        await wait_for_processes_to_run(agents)
    else:
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


def run_full_simulation(
    n_runs,
    configs,
    periodic_processes=False,
    instant_processes=False,
    agent_processes=False,
    name="python_single_process_",
):
    # Vanilla python mango
    periodic_processes = instant_processes = False
    results = {}

    for config in configs:
        result_times = [0] * n_runs

        for i in range(n_runs):
            result_times[i] = asyncio.run(
                run_simulation(
                    config, periodic_processes, instant_processes, agent_processes
                )
            )

        results[config["simulation_name"]] = result_times

    save_sim_results(results, name)


def main():
    n_runs, configs = read_parameters()

    run_full_simulation(
        n_runs,
        configs,
        periodic_processes=False,
        instant_processes=False,
        agent_processes=True,
        name="python_agent_processes_",
    )

    run_full_simulation(
        n_runs,
        configs,
        periodic_processes=False,
        instant_processes=False,
        agent_processes=False,
        name="python_single_process_",
    )

    run_full_simulation(
        n_runs,
        configs,
        periodic_processes=True,
        instant_processes=False,
        agent_processes=False,
        name="python_periodic_processes_",
    )

    run_full_simulation(
        n_runs,
        configs,
        periodic_processes=True,
        instant_processes=True,
        agent_processes=False,
        name="python_task_processes_",
    )


if __name__ == "__main__":
    main()

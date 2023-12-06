 
# General Setup
The main appeal of mango is to facilitate simple communication between agents with networking, encoding/decoding, and awaiting asynchronous operations being abstracted by scheduler and container methods.

As such, the main goal of this benchmark is test the efficiency of message handling, message passing, and task scheduling by the different implementations of mango.

The benchmark considers the following main parameters:
* MAS size and structure as given by the topology and amount of agents
* message frequency and payload size
* frequency and amount of blocking busy work within agents
* degree of parallelization (as given by amount of threads or procoesses) within each agent
* degree of containerization - how many containers and therefore network ports are accesible to the MAS

Each of these parameter sets is tested on a "basic" and a "role-based" implementation in both python and julia.

## Agent Behavior
Agent behavior is designed to simulate the interaction of internal work in the agent with its communication. Each agent performs three kinds of tasks:
* periodic busy work that is triggered as long as the agent is active
* once-off busy work that is triggered by incoming messages
* handling of and response to incoming messages

In this model, each agent is given a neighborhood of other agents. Its task is to send "ping" messages to each of its neighbours and await the corresponding "pong" messages. The amount of ping-pong cycles for an agent are given as a simulation parameter.

The agent terminates when it received the last "pong" message. The MAS terminates when all agents have terminated.

Each message triggers a batch of blocking busy work that runs in addition to the busy work it runs as long as it is active.

## Roles vs Basic Implementations
Both mango implementations support a role system to abstract various responsibilities of an agents into their own modules. These are run as separate parts of the benchmark to see if they have an impact on performance and if so why.

## Parameterization
### MAS Size
Each MAS consists of a fixed number of agents. Within this benchmark this is varied as:
* $|A| \in \{10, 100, 1000\}$

### Topology
In the described agent behavior, the topology of the MAS plays a big role in the amount of messages that need to be passed. 

To ensure scenarios (especially considering containerization) are equivalent between different runs and implementations, topology is not randomized.
Instead, we pre-define 5 fixed small-world topologies with $k \in \{0, 0.2, 0.4, 0.6, 0.8, 1\}$ for each agent amount in the parameters.

These topologies are created with a single script on a fixed random seed and the results are saved with the remaining scenario parameters.

### Messages
Messages are governed by two parameters:
* $n_m \in [10, 100]$ the number of ping-pong rounds for each neighbor
* $size_m \in [10, 1000]$ the size (in bytes) of the content of each message (ignoring any metadata)

### Work
The busy work of an agent is governed by:
* $w_{message}$ workload of tasks triggered by each incoming message
* $w_{periodic}$ workload of periodic tasks that run while active
* $n_{periodic}$ number of periodic tasks scheduled
* $d_{periodic}$ delay between repeating the same periodic task

### Threads and Processes
Python does not (as of yet) support native multi-threading as it is gated by the GIL. To circumvent this, mango can delegate tasks to different sub-processes. This part of the scenarios distributes the julia and python agent systems onto $n_threads$ threads or processes per container, respectively, to test their influence on the overall system performance.

At most, each agent in a container gets its own thread or process. 

### Degree of Containerization
* Given by a number $n_C$ of containers in the system. If $n_C \geq n_A$ then every agent has its own container. In the parameters, this is varied as:
* $|C| \in [1, 10]$

## Evaluation
In the first version of this benchmark, executions are compared by their total runtime.
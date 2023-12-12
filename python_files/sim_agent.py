import mango
import time
from dataclasses import dataclass


def busy_work(time_in_s):
    start = time.time()
    while time.time() - start < time_in_s:
        pass


@dataclass
class AgentAddress:
    """
    Dataclass for sending and receiving Agent Information
    """

    host: str
    port: int
    agent_id: str

    def __eq__(self, other):
        return (
            self.host == other.host
            and self.port == other.port
            and self.agent_id == other.agent_id
        )

    def __hash__(self):
        return hash(("host", self.host, "port", self.port, "agent_id", self.agent_id))


class SimAgent(Agent):
    def __init__(
        self,
        container,
        work_on_message_in_seconds,
        w_periodic_in_seconds,
        n_periodic_tasks,
        delay_periodic_in_seconds,
        response_count,
        message_size_bytes,
    ):
        super().__init__(container)
        self.work_on_message_in_seconds = work_on_message_in_seconds
        self.w_periodic_in_seconds = w_periodic_in_seconds
        self.n_periodic_tasks = n_periodic_tasks
        self.delay_periodic_in_seconds = delay_periodic_in_seconds
        self.response_count = response_count
        self.message_size_bytes = message_size_bytes
        self.neighbors = []
        self.neighbor_pong_future = {}

    def handle_message(self, content, meta):
        # This method defines what the agent will do with incoming messages.
        # TODO implement me

    def set_neighbors(self, neighbors):
        self.set_neighbors = neighbors

    async def start_periodic_tasks(self):
        # TODO implement me
        pass

    async def run_agent(self):
        await self.start_periodic_tasks()
        await asyncio.gather(
            *[self.run_ping_loop_for_neighbor(n) for n in self.neighbors]
        )

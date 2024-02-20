import mango
import asyncio
from mango import Agent
from mango.messages.codecs import json_serializable
import time
from dataclasses import dataclass

PING_TYPE = "ping"
PONG_TYPE = "pong"
PING_CHAR = "a"
PONG_CHAR = "b"

# schedule_instant_task(self, coroutine, on_stop=None, src=None)


@json_serializable
@dataclass
class PingMessage:
    msg_dict: dict


@json_serializable
@dataclass
class PongMessage:
    msg_dict: dict


def make_ping_message(nesting_depths, msg_bytes):
    msg_dict = {}
    data = PING_CHAR * msg_bytes
    data_dict = {"data": data}
    for i in range(nesting_depths):
        if i == 1:
            msg_dict = data_dict
        else:
            new_layer = {"data": msg_dict}
            msg_dict = new_layer

    return PingMessage(msg_dict)


def make_pong_message(nesting_depths, msg_bytes):
    msg_dict = {}
    data = PONG_CHAR * msg_bytes
    data_dict = {"data": data}
    for i in range(nesting_depths):
        if i == 1:
            msg_dict = data_dict
        else:
            new_layer = {"data": msg_dict}
            msg_dict = new_layer

    return PongMessage(msg_dict)


async def busy_work(time_in_s):
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
        message_amount,
        message_size_bytes,
        message_nesting_depths,
    ):
        super().__init__(container)
        self.work_on_message_in_seconds = work_on_message_in_seconds
        self.w_periodic_in_seconds = w_periodic_in_seconds
        self.n_periodic_tasks = n_periodic_tasks
        self.delay_periodic_in_seconds = delay_periodic_in_seconds
        self.message_amount = message_amount
        self.message_size_bytes = message_size_bytes
        self.message_nesting_depths = message_nesting_depths
        self.neighbors = []  # list of agent adresses
        self.neighbor_pong_future = {}
        self.incoming_message_count = 0

    async def periodic_work(self):
        await busy_work(self.w_periodic_in_seconds)

    async def message_work(self):
        await busy_work(self.work_on_message_in_seconds)

    def handle_message(self, content, meta):
        self.incoming_message_count += 1
        sender_id = meta.get("sender_id", None)
        sender_addr = meta.get("sender_addr", None)
        sender = AgentAddress(sender_addr[0], sender_addr[1], sender_id)

        # work
        # self.schedule_instant_task(self.message_work())
        if isinstance(content, PingMessage):
            self.send_pong(sender)
        elif isinstance(content, PongMessage):
            self.neighbor_pong_future[sender].set_result(True)

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def start_periodic_tasks(self):
        for _ in range(self.n_periodic_tasks):
            # self.schedule_periodic_task(
            #     self.periodic_work(), self.delay_periodic_in_seconds
            # )
            pass

    async def run_agent(self):
        self.start_periodic_tasks()
        await asyncio.gather(
            *[self.run_ping_loop_for_neighbor(n) for n in self.neighbors]
        )

    def send_ping(self, receiver):
        data = make_ping_message(self.message_nesting_depths, self.message_size_bytes)
        acl_meta = {"sender_id": self.aid, "sender_addr": self.addr}
        self.schedule_instant_acl_message(
            data,
            (receiver.host, receiver.port),
            receiver.agent_id,
            acl_metadata=acl_meta,
        )

    def send_pong(self, receiver):
        data = make_pong_message(self.message_nesting_depths, self.message_size_bytes)
        acl_meta = {"sender_id": self.aid, "sender_addr": self.addr}
        self.schedule_instant_acl_message(
            data,
            (receiver.host, receiver.port),
            receiver.agent_id,
            acl_metadata=acl_meta,
        )

    async def run_ping_loop_for_neighbor(self, neighbor):
        for _ in range(self.message_amount):
            self.send_ping(neighbor)
            self.neighbor_pong_future[neighbor] = asyncio.Future()
            await self.neighbor_pong_future[neighbor]

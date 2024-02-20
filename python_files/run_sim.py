import asyncio
from sim_agent import SimAgent, PingMessage, PongMessage, AgentAddress
from mango import create_container
from mango.messages.codecs import JSON


async def main():
    codec = JSON()
    codec.add_serializer(*PingMessage.__serializer__())
    codec.add_serializer(*PongMessage.__serializer__())

    # TODO dont forget to add message classes to codecs
    c = await create_container(addr=("localhost", 5555), codec=codec)
    a1 = SimAgent(c, 1, 1, 1, 1, 2, 10, 5)
    a2 = SimAgent(c, 1, 1, 1, 1, 2, 10, 5)

    a1_addr = AgentAddress("localhost", 5555, "agent0")
    a2_addr = AgentAddress("localhost", 5555, "agent1")

    a1.set_neighbors([a2_addr])
    a2.set_neighbors([a1_addr])

    await asyncio.gather(*[a1.run_agent(), a2.run_agent()])

    print(a1.incoming_message_count)
    print(a2.incoming_message_count)

    await c.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

module SimulationAgent
using Mango
import Mango.AgentCore.handle_message
using Sockets: InetAddr
using OrderedCollections

export SimAgent, AgentAddress, run_agent

PING_TYPE = "ping"
PONG_TYPE = "pong"
PING_CHAR = 'a'
PONG_CHAR = 'b'

struct AgentAddress
    addr::InetAddr
    aid::String

    function AgentAddress(msg_addr::InetAddr, msg_aid::String)
        return new(msg_addr, msg_aid)
    end

    function AgentAddress(msg_addr::String, msg_aid::String)
        host, port_string = split(msg_addr, ":")
        port = parse(UInt16, port_string)

        return new(InetAddr(host, port), msg_aid)
    end
end


@agent struct SimAgent
    work_on_message_in_seconds::Float64
    w_periodic_in_seconds::Float64
    n_periodic_tasks::Int64
    delay_periodic_in_seconds::Float64
    response_count::Int64
    message_size_bytes::Int64
    neighbors::Vector{AgentAddress}
    #neighbor_pongs_received::Dict{AgentAddress,Int64}
    neighbor_pong_future::Dict{AgentAddress,Condition}
end

function send_ping(agent::SimAgent, target::AgentAddress)
    data = PING_CHAR^agent.message_size_bytes
    send_message(agent, data, target.aid, target.addr, type=PING_TYPE)
    agent.neighbor_pong_future[target] = Condition()
end

function send_pong(agent::SimAgent, target::AgentAddress)
    data = PONG_CHAR^agent.message_size_bytes
    send_message(agent, data, target.aid, target.addr, type=PONG_TYPE)
end

# Override the default handle_message function for ping pong agents
function handle_message(agent::SimAgent, content::Any, meta::AbstractDict)
    # All messages should contain the following <meta> fields:
    #
    # - "sender_id" --- aid of the sending agent
    # - "sender_addr" --- address of the sending agents container
    # - "type" --- {"ping" or "pong"}
    #
    # The <content> field itself contains the payload of predefined size.
    # We don't do anything with that.
    println("got a message with: ", content, "  ", meta)

    sender = AgentAddress(meta["sender_addr"], meta["sender_id"])

    # TODO schedule once off busy work

    if meta["type"] == PING_TYPE
        send_pong(agent, sender)
    elseif meta["type"] == PONG_TYPE
        notify(agent.neighbor_pong_future[sender])
    end
end

# central entry point to start doing the agents work post initialization
function run_agent(agent::SimAgent)::Nothing
    @async start_periodic_tasks(agent)

    # @sync for neighbor in agent.neighbors
    #     @async run_ping_loop_for_neighbor(agent, neighbor)
    # end

    for neighbor in agent.neighbors
        run_ping_loop_for_neighbor(agent, neighbor)
    end
end

function start_periodic_tasks(agent::SimAgent)::Nothing
    # TODO implement me
end

function run_ping_loop_for_neighbor(agent::SimAgent, neighbor::AgentAddress)::Nothing
    for _ = 1:agent.response_count
        send_ping(agent, neighbor)
        wait(agent.neighbor_pong_future[neighbor])
    end
end

#
# All the work simulation mechanisms
#
function busy_work(t_in_seconds::Float64)::Nothing
    start = time()
    while time() - start < t_in_seconds
    end
    return nothing
end

function schedule_periodic_task(agent::SimAgent)

end

function schedule_one_off_task(agent::SimAgent)

end

end
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
    work_periodic_in_seconds::Float64
    n_periodic_tasks::Int64
    delay_periodic_in_seconds::Float64
    message_amount::Int64
    message_size_bytes::Int64
    message_nesting_depths::Int64

    # non-config fields
    neighbors::Vector{AgentAddress}
    neighbor_pong_future::Dict{AgentAddress,Threads.Condition}
    incoming_msg_count::Int64 # for debugging only
end

function send_ping(agent::SimAgent, target::AgentAddress)
    msg_dict = Dict{String,Dict}()
    data_dict = Dict{String,String}()
    data_dict["data"] = PING_CHAR^agent.message_size_bytes

    for i = 1:agent.message_nesting_depths
        if i == 1
            msg_dict = data_dict
        else
            new_layer = Dict{String,Dict}()
            new_layer["data"] = msg_dict
            msg_dict = new_layer
        end
    end

    send_message(agent, msg_dict, target.aid, target.addr, type = PING_TYPE)
end

function send_pong(agent::SimAgent, target::AgentAddress)
    msg_dict = Dict{String,Dict}()
    data_dict = Dict{String,String}()
    data_dict["data"] = PONG_CHAR^agent.message_size_bytes

    for i = 1:agent.message_nesting_depths
        if i == 1
            msg_dict = data_dict
        else
            new_layer = Dict{String,Dict}()
            new_layer["data"] = msg_dict
            msg_dict = new_layer
        end
    end

    send_message(agent, msg_dict, target.aid, target.addr, type = PONG_TYPE)
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
    # println("got a message with: ", content, "  ", meta)
    agent.incoming_msg_count += 1
    sender = AgentAddress(meta["sender_addr"], meta["sender_id"])

    # simulate work caused by the message
    schedule_one_off_task(agent)

    if meta["type"] == PING_TYPE
        send_pong(agent, sender)
    elseif meta["type"] == PONG_TYPE
        lock(agent.neighbor_pong_future[sender]) do
            notify(agent.neighbor_pong_future[sender])
        end
    end
end

# central entry point to start doing the agents work post initialization
function run_agent(agent::SimAgent)::Nothing
    @async start_periodic_tasks(agent)

    @sync for neighbor in agent.neighbors
        Threads.@spawn run_ping_loop_for_neighbor(agent, neighbor)
    end
end

function start_periodic_tasks(agent::SimAgent)::Nothing
    for _ = 1:agent.n_periodic_tasks
        schedule_periodic_task(agent)
    end
end

function run_ping_loop_for_neighbor(agent::SimAgent, neighbor::AgentAddress)::Nothing
    for _ = 1:agent.message_amount
        send_ping(agent, neighbor)
        agent.neighbor_pong_future[neighbor] = Threads.Condition()
        lock(agent.neighbor_pong_future[neighbor]) do
            wait(agent.neighbor_pong_future[neighbor])
        end
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

function schedule_periodic_task(agent::SimAgent)::Nothing
    function periodic_task()
        busy_work(agent.work_periodic_in_seconds)
    end
    schedule(periodic_task, agent, PeriodicTaskData(agent.delay_periodic_in_seconds))
    return nothing
end

function schedule_one_off_task(agent::SimAgent)::Nothing
    function one_off_task()
        busy_work(agent.work_on_message_in_seconds)
    end
    schedule(one_off_task, agent, InstantTaskData())
    return nothing
end

end
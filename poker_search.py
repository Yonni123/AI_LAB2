import poker_game_example as pg_
from poker_game_example import PokerPlayer, GameState
import igraph as ig
import matplotlib.pyplot as plt
import heapq


# just to display some colors
class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

#context param
MAX_HANDS = 4
INIT_AGENT_STACK = 400
MAX_BIDDS = 3
MAX_NODES = 100
MAX_DEPTH = 10


class PriorityQueue:
    def __init__(self):
        self.elements = []
        self.counter = 0  # counter for tie breaking

    def isEmpty(self):
        return len(self.elements) == 0

    def add(self, item, priority):
        # print((priority, item))
        t = (priority, self.counter, item)
        heapq.heappush(self.elements, t)
        self.counter += 1

    def remove(self):
        return heapq.heappop(self.elements)[2]

    def removeWPrio(self):
        return heapq.heappop(self.elements)


#create the players
def create_player():
    agent = PokerPlayer(
        current_hand_=None,
        stack_=INIT_AGENT_STACK,
        action_=None,
        action_value_=None
    )
    opponent = PokerPlayer(
        current_hand_=None, stack_=INIT_AGENT_STACK, action_=None, action_value_=None
    )
    return (agent, opponent)


def initialize_game():
    agent, opponent = create_player()
    init_state = GameState(
        nn_current_hand_=0,
        nn_current_bidding_=0,
        phase_="INIT_DEALING",
        pot_=0,
        acting_agent_=None,
        agent_=agent,
        opponent_=opponent,
    )
    return (init_state, agent, opponent)


def tree_print(game_state, l, d=0):
    if game_state.phase != "INIT_DEALING":
        l.append(
            [
                game_state._id,
                game_state.agent.action,
                d,
                game_state.parent_state._id,
                "A" if game_state.acting_agent == "agent" else "O",
                game_state.nn_current_hand,
                game_state.agent.stack,
            ]
        )
    else:
        (
            l.append(
                [game_state._id, "INIT", d, -1, "I", game_state.nn_current_hand, 400]
            )
        )
    for child in game_state.children:
        l = tree_print(child, l, d + 1)
    return l


def winnings_hueristic(state):
    return state.opponent.stack / state.agent.stack


def poker_search_sorted(init_state, state_queue, info):
    end_state = None
    max_n = info["max_nodes"]
    max_b = info["max_bidds"]
    max_h = info["max_hands"]
    nn_nodes = 0
    w_cond_found = False
    stateQ = PriorityQueue()
    stateQ.add(init_state, 0)
    while not stateQ.isEmpty():
        c_state = stateQ.remove()
        if c_state.phase == "SHOWDOWN" and c_state.agent.stack <= 300:
            if stateQ.isEmpty():
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state

                break
        elif c_state.phase == "SHOWDOWN" and c_state.opponent.stack <= 300:
            end_state = c_state
            w_cond_found = True
            print("Win condition found (DFS)")
            break
        elif c_state.phase == "SHOWDOWN" and c_state.nn_current_hand >= max_h:
            if stateQ.isEmpty():
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "BIDDING" and c_state.nn_current_bidding >= max_b:
            if stateQ.isEmpty():
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                print("Bidding limit reached")
                break
        else:
            n_states = pg_.get_next_states(c_state)
            nn_nodes += len(n_states)
            for n_state in n_states:
                stateQ.add(n_state, winnings_hueristic(n_state))
        if nn_nodes >= max_n:
            print("Max nodes reached")
            break
    return init_state, end_state, w_cond_found, nn_nodes


def poker_search_dfs(init_state, state_queue, info):
    end_state = None
    max_n = info["max_nodes"]
    max_b = info["max_bidds"]
    max_h = info["max_hands"]
    nn_nodes = 0
    w_cond_found = False
    while len(state_queue) != 0:
        c_state = state_queue.pop(-1)
        if c_state.phase == "SHOWDOWN" and c_state.agent.stack <= 300:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "SHOWDOWN" and c_state.opponent.stack <= 300:
            end_state = c_state
            w_cond_found = True
            print("Win condition found (DFS)")
            break
        elif c_state.phase == "SHOWDOWN" and c_state.nn_current_hand >= max_h:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "BIDDING" and c_state.nn_current_bidding >= max_b:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                print("Bidding limit reached")
                break
        else:
            n_states = pg_.get_next_states(c_state)
            nn_nodes += len(n_states)
            state_queue.extend(n_states)
        if nn_nodes >= max_n:
            print("Max nodes reached")
            break
    return init_state, end_state, w_cond_found, nn_nodes


def poker_search_bfs(init_state, state_queue, info):
    end_state = None
    max_n = info["max_nodes"]
    max_b = info["max_bidds"]
    max_h = info["max_hands"]
    nn_nodes = 0
    w_cond_found = False
    while len(state_queue) != 0:
        c_state = state_queue.pop(0)
        if c_state.phase == "SHOWDOWN" and c_state.agent.stack <= 300:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "SHOWDOWN" and c_state.opponent.stack <= 300:
            end_state = c_state
            w_cond_found = True
            print("Win condition found (BFS)")
            break
        elif c_state.phase == "SHOWDOWN" and c_state.nn_current_hand >= max_h:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "BIDDING" and c_state.nn_current_bidding >= max_b:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                print("Bidding limit reached")
                break
        else:
            n_states = pg_.get_next_states(c_state)
            nn_nodes += len(n_states)
            state_queue.extend(n_states)
        if nn_nodes >= max_n:
            print("Max nodes reached")
            break
    return init_state, end_state, w_cond_found, nn_nodes


def poker_search(
        max_hands=MAX_HANDS,
        max_bidds=MAX_BIDDS,
        max_nodes=MAX_NODES,
        max_depth=MAX_DEPTH,
        search_function=poker_search_dfs,
):
    init_state, agent, opponent = initialize_game()
    state_queue = [init_state]
    info = {
        "max_hands": max_hands,
        "max_bidds": max_bidds,
        "max_nodes": max_nodes,
        "max_depth": max_depth,
    }
    return search_function(init_state, state_queue, info)

    while len(state_queue) != 0:
        c_state = state_queue.pop(-1)
        if c_state.phase == "SHOWDOWN" and (
                c_state.opponent.stack <= 300 or c_state.agent.stack <= 300
        ):
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "SHOWDOWN" and c_state.nn_current_hand >= max_hands:
            if len(state_queue) == 0:
                print("All nodes reached")
                print(nn_nodes)
                end_state = c_state
                break
        elif c_state.phase == "BIDDING" and c_state.nn_current_bidding >= max_bidds:
            print("Bidding limit reached")
        else:
            n_states = pg_.get_next_states(c_state)
            nn_nodes += len(n_states)
            state_queue.extend(n_states)
        if nn_nodes >= max_nodes:
            print("Max nodes reached")
            break
    return init_state, end_state


def print_winning_path(end_state):
    state = end_state
    winning_path = [end_state]
    while state.parent_state != None:
        state = state.parent_state
        winning_path.append(state)
    lenght = len(winning_path) - 1
    for step in range(len(winning_path)):
        st = winning_path[lenght - step]
        if st.phase == "INIT_DEALING":
            print(str(step) + f" : {bcolors.WARNING}START DEALING{bcolors.ENDC}" + "\n")
        else:
            print(str(step) + " : " + (f"{bcolors.OKGREEN}Agent{bcolors.ENDC}" if st.acting_agent == "agent" else f"{bcolors.OKBLUE}Opponent{bcolors.ENDC}"))
            print("Action: " + st.agent.action if st.acting_agent == "agent" else st.opponent.action)
            print("Phase: " + st.phase)
            print("Stack: " + str(st.agent.stack) + '\n')
    print(f"Lenght of the winning path is {bcolors.FAIL}" + str(lenght) + f"{bcolors.ENDC}\n")

def plot_tree(l, w_state=None):

    edges = []
    for node in l:
        if node[3] != -1:
            edges.append((node[3], node[0]))

    n_vertices = len(l)
    g = ig.Graph(n_vertices, edges)
    for node in l:
        g.vs[node[0]]["Action"] = str(node[5]) + ": " + node[1] + "\n" + str(node[6])
        g.vs[node[0]]["Depth"] = node[2]
        g.vs[node[0]]["Agent"] = node[4]
        if w_state != None:
            if node[0] == w_state:
                g.vs[node[0]]["Win"] = True
            else:
                g.vs[node[0]]["Win"] = False

    fig, ax = plt.subplots(figsize=(5, 5))
    layout = g.layout_reingold_tilford(root=[0])
    layout.rotate(180)
    if w_state != None:
        vcol = [
            "#8888FF" if agent == "A" else ("#FF8888" if agent == "O" else "#88FF88")
            for agent in g.vs["Agent"]
        ]
        vcol[w_state] = "#f542e9"
    else:
        vcol = [
            "#8888FF" if agent == "A" else ("#FF8888" if agent == "O" else "#88FF88")
            for agent in g.vs["Agent"]
        ]

    ig.plot(
        g,
        target=ax,
        # print nodes in a circular layout
        layout=layout,
        vertex_size=0.5,
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        vertex_label=g.vs["Action"],
        vertex_label_size=12.0,
        vertex_color=vcol,
    )

    plt.show()


def print_winning_path(end_state):
    state = end_state
    winning_path = [end_state]
    while state.parent_state != None:
        state = state.parent_state
        winning_path.append(state)
    lenght = len(winning_path) - 1
    for step in range(len(winning_path)):
        st = winning_path[lenght - step]
        if st.phase == "INIT_DEALING":
            print(f"\n{bcolors.WARNING}", str(step) + " : START DEALING", f"{bcolors.ENDC}")
        else:
            print(str(step) + " : " + ("Agent :" if st.acting_agent == "agent" else "Opponent :"))
            print("Action: " + st.agent.action if st.acting_agent == "agent" else st.opponent.action)
            print("Phase: " + st.phase)
            print("Stack = " + str(st.agent.stack), "\n")
    print(f"The lenght of the winning path is{bcolors.FAIL}", lenght, f"{bcolors.ENDC}\n")

MAX_PLOT = 100
plotting = False
init_state_dfs, end_state_dfs, w_cond_found_dfs, nodes_dfs = poker_search(
    max_nodes=100000, max_depth=20, max_bidds=7, search_function=poker_search_dfs
)

init_state_bfs, end_state_bfs, w_cond_found_bfs, nodes_bfs = poker_search(
    max_nodes=1000000, max_depth=20, max_bidds=7, search_function=poker_search_bfs
)

init_state_s, end_state_s, w_cond_found_s, nodes_s = poker_search(
    max_nodes=1000000, max_depth=20, max_bidds=7, search_function=poker_search_sorted
)

l = []
if w_cond_found_dfs == True:
    print(f"{bcolors.OKCYAN}Depth-first path{bcolors.ENDC}")
    print_winning_path(end_state_dfs)
if w_cond_found_bfs == True:
    print(f"{bcolors.OKCYAN}Breadth-first path{bcolors.ENDC}")
    print_winning_path(end_state_bfs)
if w_cond_found_s == True:
    print(f"{bcolors.OKCYAN}Sorted search path{bcolors.ENDC}")
    print_winning_path(end_state_s)
print(f"Nodes explored by Depth-First Search :{bcolors.OKCYAN}", nodes_dfs, f"{bcolors.ENDC}")
print(f"Nodes explored by Breadth-First Search :{bcolors.OKCYAN}", nodes_bfs, f"{bcolors.ENDC}")
print(f"Nodes explored by s :{bcolors.OKCYAN}", nodes_s, f"{bcolors.ENDC}")

if plotting:
    l = tree_print(init_state_bfs, l)
    if w_cond_found_bfs:
        plot_tree(l[:MAX_PLOT], w_state=end_state_bfs._id)
    else:
        plot_tree(l[:MAX_PLOT])
#Set attributes for the graph, nodes, and edges
# g["title"] = "Small Social Network"
# g.vs["name"] = ["Daniel Morillas", "Kathy Archer",
#                "Kyle Ding", "Joshua Walton", "Jana Hoyer"]
# g.vs["gender"] = ["M", "F", "F", "M", "F"]


# Set individual attributes
# g.vs[1]["name"] = "Kathy Morillas"
# g.es[0]["married"] = True

# Plot in matplotlib
# Note that attributes can be set globally (e.g. vertex_size), or set individually using arrays (e.g. vertex_color)


# Plot in plotly

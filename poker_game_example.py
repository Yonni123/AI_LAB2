import poker_environment as pe_
from poker_environment import AGENT_ACTIONS, BETTING_ACTIONS
import copy

MAX_BIDDING: int = 5


def gen_get_unique_GSID() -> int:
    GSID: int = 0

    while True:
        yield GSID
        GSID += 1


get_unique_GSID = gen_get_unique_GSID()


class PokerPlayer(object):
    """
    Player class representing a poker agent to be playing into the described poker game
    """

    def __init__(
        self, current_hand_=None, stack_=300, action_=None, action_value_=None
    ):
        self.current_hand = current_hand_
        self.current_hand_type = []
        self.current_hand_strength = []
        self.stack = stack_
        self.action = action_
        self.action_value = action_value_

    def evaluate_hand(self) -> None:
        """
        Identify agent hand and evaluate it's strength.
        - Stores hand type into 'self.current_hand_type'.
        - Stores hand strength score into 'self.current_hand_strength'.
        """

        self.current_hand_type = pe_.identify_hand(self.current_hand)
        self.current_hand_strength = (
            pe_.Types[self.current_hand_type[0]] * len(pe_.Ranks)
            + pe_.Ranks[self.current_hand_type[1]]
        )

    def get_actions(self) -> set[str]:
        """
        Returns possible actions
        - FOLD if there is not enough money...
        """

        actions_ = []
        for _action_ in AGENT_ACTIONS:  # AGENT_ACTIONS is shuffled when imported lmao
            # Checking that agent has enough money to bet BETN amount. If not => FOLD
            if _action_[:3] == "BET" and int(_action_[3:]) >= (self.stack):
                actions_.append("FOLD")
            else:
                actions_.append(_action_)
        return set(actions_)


class GameState(object):
    """
    Game state class containing data about a phase of a poker game.

    i.e.:
        - Who played this phase of the game ?
        - Was it card dealing phase ?
    """

    def __init__(
        self,
        nn_current_hand_: int = None,
        nn_current_bidding_: int = None,
        phase_: str = None,
        pot_: int = None,
        acting_agent_: str = None,
        parent_state_: "GameState" = None,
        children_state_: list["GameState"] = [],  # list ?
        agent_: PokerPlayer = None,
        opponent_: PokerPlayer = None,
        depth_: int = 0,
    ):
        """
        Initializes a game state with the provided information
        """
        self.nn_current_hand = nn_current_hand_
        self.nn_current_bidding = nn_current_bidding_
        self.phase = phase_
        self.pot = pot_
        self.acting_agent = acting_agent_
        self.parent_state: GameState = parent_state_
        self.children = children_state_
        self.agent = agent_
        self.opponent = opponent_
        self.showdown_info = None
        self.depth = depth_
        self._id: int = next(get_unique_GSID)

    def dealing_cards(self) -> None:
        """
        draw 10 cards randomly from a deck
        """
        if self.nn_current_hand >= 20:
            print("random hand  ", self.nn_current_hand)
            # randomly generated hands
            agent_hand, opponent_hand = pe_.generate_2hands()
        else:
            # fixed_hands or use the function below
            print("fixed hand ", self.nn_current_hand)
            agent_hand, opponent_hand = pe_.fixed_hands[self.nn_current_hand]
        self.agent.current_hand = agent_hand
        self.agent.evaluate_hand()
        self.opponent.current_hand = opponent_hand
        self.opponent.evaluate_hand()

    def dealing_cards_fixed(self) -> None:
        """
        draw 10 cards from a fixed sequence of hands
        """
        # print("Fixed hand nr:", self.nn_current_hand)
        self.agent.current_hand = pe_.fixed_hands[self.nn_current_hand][0]
        self.agent.evaluate_hand()
        self.opponent.current_hand = pe_.fixed_hands[self.nn_current_hand][1]
        self.opponent.evaluate_hand()

    def showdown(self) -> None:
        """
        SHOWDOWN phase, assign pot to players
        """
        # Draw case
        if self.agent.current_hand_strength == self.opponent.current_hand_strength:
            self.showdown_info = "draw"
            if self.acting_agent == "agent":
                self.agent.stack += (self.pot - 5) / 2.0 + 5
                self.opponent.stack += (self.pot - 5) / 2.0
            else:
                self.agent.stack += (self.pot - 5) / 2.0
                self.opponent.stack += (self.pot - 5) / 2.0 + 5
        # If agent wins
        elif self.agent.current_hand_strength > self.opponent.current_hand_strength:
            self.showdown_info = "agent win"
            self.agent.stack += self.pot
        # If opponent win
        else:
            self.showdown_info = "opponent win"
            self.opponent.stack += self.pot

    def print_state_info(self):
        """
        Prints out necessary information of this game state.
        """

        print("************* state info **************")
        print("nn_current_hand", self.nn_current_hand)
        print("nn_current_bidding", self.nn_current_bidding)
        print("phase", self.phase)
        print("pot", self.pot)
        print("acting_agent", self.acting_agent)
        print("parent_state", self.parent_state)
        print("children", self.children)
        print("agent", self.agent)
        print("opponent", self.opponent)

        if self.phase == "SHOWDOWN":
            print("---------- showdown ----------")
            print("agent.current_hand", self.agent.current_hand)
            print(self.agent.current_hand_type, self.agent.current_hand_strength)
            print("opponent.current_hand", self.opponent.current_hand)
            print(self.opponent.current_hand_type, self.opponent.current_hand_strength)
            print("showdown_info", self.showdown_info)

        print("----- agent -----")
        print("agent.current_hand", self.agent.current_hand)
        print("agent.current_hand_type", self.agent.current_hand_type)
        print("agent.current_hand_strength", self.agent.current_hand_strength)
        print("agent.stack", self.agent.stack)
        print("agent.action", self.agent.action)
        print("agent.action_value", self.agent.action_value)

        print("----- opponent -----")
        print("opponent.current_hand", self.opponent.current_hand)
        print("opponent.current_hand_type", self.opponent.current_hand_type)
        print("opponent.current_hand_strength", self.opponent.current_hand_strength)
        print("opponent.stack", self.opponent.stack)
        print("opponent.action", self.opponent.action)
        print("opponent.action_value", self.opponent.action_value)
        print("**************** end ******************")


def copy_state(game_state: GameState, remove_relatives: bool = True) -> GameState:
    """
    Copies the given state in the argument
    """
    _state = copy.copy(game_state)
    _state.agent = copy.copy(game_state.agent)
    _state.opponent = copy.copy(game_state.opponent)
    _state._id = next(get_unique_GSID)
    _state.depth += 1

    if remove_relatives:
        _state.parent_state = None
        _state.children.clear()

    return _state


def get_next_states(last_state: GameState) -> list[GameState]:
    """
    Successor function for generating next state(s)
    """

    states = []

    if (  # Time for agent to play (bet)
        last_state.phase in ["SHOWDOWN", "INIT_DEALING"]
        or last_state.acting_agent == "opponent"
    ):
        # NEW BETTING ROUND, AGENT ACTS FIRST
        for _action_ in last_state.agent.get_actions():
            _state_ = copy_state(last_state)
            _state_.acting_agent = "agent"
            # print("agent action: ", _action_)
            # Deal new cards if starting a new game
            if last_state.phase in ["SHOWDOWN", "INIT_DEALING"]:
                _state_.dealing_cards_fixed()  # Uselessly called 5 times :(
                # _state_.dealing_cards()

            # When agent chooses to call, automatically proceed to showdown
            if _action_ == "CALL":
                # Sets up game state to showdown phase
                _state_.phase = "SHOWDOWN"
                _state_.agent.action = _action_
                _state_.agent.action_value = 5
                _state_.agent.stack -= 5
                _state_.pot += 5
                # Proceed to showdown
                _state_.showdown()
                # Resets state for next game...
                _state_.nn_current_hand += 1
                _state_.nn_current_bidding = 0
                _state_.pot = 0
                _state_.parent_state = last_state
                states.append(_state_)

            # When agent chooses to fold (give up)
            elif _action_ == "FOLD":
                # Sets up game state to (FOLD) SHOWDOWN phase
                _state_.phase = "SHOWDOWN"
                _state_.agent.action = _action_
                _state_.opponent.stack += _state_.pot  # Give pot to opponent
                # Reset state for next game
                _state_.nn_current_hand += 1
                _state_.nn_current_bidding = 0
                _state_.pot = 0
                _state_.parent_state = last_state
                states.append(_state_)

            # When agent chooses to bet more on the current game
            elif _action_ in BETTING_ACTIONS:
                if _state_.nn_current_bidding > MAX_BIDDING:
                    continue
                # Sets up bidding state
                _bidding_amount: int = int(_action_[3:])  # Bidding amount
                _state_.phase = "BIDDING"
                _state_.agent.action = _action_
                _state_.agent.action_value = (
                    _bidding_amount  # Save bidding value into state
                )
                _state_.agent.stack -= _bidding_amount  # Remove bid from agent stack
                _state_.pot += _bidding_amount  # Adds bid amount to pot

                _state_.nn_current_bidding += 1
                _state_.parent_state = last_state
                states.append(_state_)

            # Error management
            else:
                print("...unknown action...")
                exit()
            # Add state to state list

        last_state.children = states

    # Opponent playing...
    elif last_state.phase == "BIDDING" and last_state.acting_agent == "agent":
        _state_ = copy_state(last_state)
        _state_.acting_agent = "opponent"

        # Opponent strategy
        opponent_action, opponent_action_value = pe_.poker_strategy_example(
            last_state.opponent.current_hand_type[0],
            last_state.opponent.current_hand_type[1],
            last_state.opponent.stack,
            last_state.agent.action,
            last_state.agent.action_value,
            last_state.agent.stack,
            last_state.pot,
            last_state.nn_current_bidding,
        )

        # Opponent calling
        if opponent_action == "CALL":
            _state_.phase = "SHOWDOWN"
            _state_.opponent.action = opponent_action
            _state_.opponent.action_value = 5
            _state_.opponent.stack -= 5
            _state_.pot += 5

            _state_.showdown()

            _state_.nn_current_hand += 1
            _state_.nn_current_bidding = 0
            _state_.pot = 0
            _state_.parent_state = last_state
            states.append(_state_)
        # Opponent folding
        elif opponent_action == "FOLD":

            _state_.phase = "SHOWDOWN"

            _state_.opponent.action = opponent_action
            _state_.agent.stack += _state_.pot

            _state_.nn_current_hand += 1
            _state_.nn_current_bidding = 0
            _state_.pot = 0
            _state_.parent_state = last_state
            states.append(_state_)
        # Opponent betting
        elif opponent_action + str(opponent_action_value) in BETTING_ACTIONS:

            _state_.phase = "BIDDING"

            _state_.opponent.action = opponent_action
            _state_.opponent.action_value = opponent_action_value
            _state_.opponent.stack -= opponent_action_value
            _state_.pot += opponent_action_value

            _state_.nn_current_bidding += 1
            _state_.parent_state = last_state
            states.append(_state_)
        # Error management
        else:
            print("unknown_action")
            exit()

        # len(states) == 1 when opponent is playing
        last_state.children = states

    return states


def print_state_tree(tree: GameState, depth=0, index=0, array: list = []) -> list:
    def _get_sub_array(_tree: GameState):
        return [
            _tree._id,  # id
            depth,  # depth
            _tree.phase,  # phase type
            _tree.agent.action if _tree.agent.action != None else "None",  # action type
            str(_tree.children.__len__()),  # number of children
        ]

    # Display which type of actions has children
    if tree.agent.action != None and tree.children.__len__() != 0:
        print("Action with children:", tree.agent.action)

    array.append(_get_sub_array(_tree=tree))
    k = index

    # if False:
    #     print(f"id : {tree._id}")
    #     print(
    #         f"\tchildren ids : {None if tree.children.__len__()==0 else [c._id for c in tree.children]}"
    #     )
    #     print(f"\tdepth : {depth}\n")
    #     print(f"\tpot: {tree.pot}\n")

    for child in tree.children:
        array = print_state_tree(child, depth + 1, k + 1, array)
        k += 1

    if depth == 0:  # Only if we are back to root node
        max_depth = max([node[1] for node in array])
        rows = [""] * (max_depth + 1)

        print("Arr len: ", len(array))

        for node in array:
            rows[node[1]] += (
                "{id="
                + str(node[0])
                + ", p="
                + node[2]
                + ", a="
                + node[3]
                + ", c="
                + node[4]
                + "} "
                + ", "
            )
        for i in range(len(rows)):
            print("D = " + str(i) + " : [" + rows[i] + "]")

    return array


"""
Game flow:
Two agents will keep playing until one of them lose 100 coins or more.
"""
if __name__ == "__main__":
    MAX_HANDS = 4
    INIT_AGENT_STACK = 400

    # initialize 2 agents and a game_state
    agent = PokerPlayer(
        current_hand_=None, stack_=INIT_AGENT_STACK, action_=None, action_value_=None
    )
    opponent = PokerPlayer(
        current_hand_=None, stack_=INIT_AGENT_STACK, action_=None, action_value_=None
    )

    init_state = GameState(
        nn_current_hand_=0,
        nn_current_bidding_=0,
        phase_="INIT_DEALING",
        pot_=0,
        acting_agent_=None,
        agent_=agent,
        opponent_=opponent,
    )

    game_state_queue = []
    game_on = True
    round_init = True

    # Game Loop
    turns = 0
    break_early = False
    game_state_history = []
    while game_on:
        # if(turns >= len(pe_.fixed_hands)):
        #    end_state_ = game_state_queue[-1]
        #    break_early = True
        #    break

        if round_init:  # Initialisation
            round_init = False
            states_ = get_next_states(init_state)
            game_state_queue.extend(states_[:])
            # print("States len: ", len(states_))
            # print("States queue len: ", len(game_state_queue))
        else:
            # just an example: only expanding the last return node
            # state[i] = {}
            # and game_state_queue[-1].phase == "SHOWDOWN"):
            if game_state_queue[-1].nn_current_hand >= MAX_HANDS:
                end_state_ = game_state_queue.pop(-1)
                print("Removed: ")
                if game_state_queue.__len__() == 0:
                    print("Game end: empty")
                    break
                continue

            # states_ = get_next_states(states_[-1])
            lState = game_state_queue.pop(-1)
            print("Hand count: ", lState.nn_current_hand)
            if turns >= 4000:
                end_state_ = lState
                print("FAIL")
                break
            lState.print_state_info()
            states_ = get_next_states(lState)
            # game_state_queue.extend(states_[:])
            game_state_history.append(lState)
            for _state_ in states_:
                if _state_.nn_current_hand <= MAX_HANDS:
                    game_state_queue.append(_state_)
                if _state_ in game_state_history:
                    print("Already in history")
                    break

            if game_state_queue.__len__() == 0:
                end_state_ = lState
                print("Game end: empty")
                break
            # print("searched: ", turns)
            # print("States len: ", len(states_))
            print("States queue len: ", len(game_state_queue))

        turns += 1

    """
    Printing game flow & info
    """

    state__ = end_state_
    nn_level = 0
    if False:
        print("------------ print game info ---------------")
        print("nn_states_total", len(game_state_queue))

        init_state.print_state_info()
        while state__.parent_state != None:
            nn_level += 1
            print(nn_level)
            # state__.print_state_info()
            state__ = state__.parent_state

        print(nn_level)
        print("\n")
    # print_state_tree(init_state)

    # if break_early:
    #    print("Game ended early")
    # else:
    #    print("Game ended normally")
    # print("end state id", end_state_._id)
    """
    Perform searches
    """

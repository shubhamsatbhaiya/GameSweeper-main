import copy

class MDP:
    def __init__(self, board, probabilities, depth=2):
        self.initial_board = board
        self.probabilities = probabilities
        self.depth = depth

    def get_state(self, board):
        # Encode state as a tuple of revealed/flagged info
        state_repr = []
        for y in range(board.height):
            for x in range(board.width):
                c = board.grid[y][x]
                state_repr.append((c.revealed, c.flagged))
        return tuple(state_repr)

    def available_actions(self, board):
        actions = []
        for c in board.get_unrevealed_cells():
            actions.append(("reveal", c.x, c.y))
            # Flagging is another option, but may not give immediate reward
            # It might help reduce uncertainty though.
            actions.append(("flag", c.x, c.y))
        return actions

    def simulate_action(self, board, action):
        # Return a copy of the board after the action is applied
        new_board = copy.deepcopy(board)
        act_type, x, y = action
        if act_type == "reveal":
            new_board.reveal_cell(x, y)
        elif act_type == "flag":
            new_board.flag_cell(x, y)
        return new_board

    def action_reward(self, board, action):
        # For reveal:
        # Reward = expected value: (1 - p_mine)*1 + p_mine*(-10)
        # For flag:
        # Reward = small neutral (0) since it's strategic not immediate.
        act_type, x, y = action
        p_mine = self.probabilities.get((x, y), 0.5)
        if act_type == "reveal":
            return (1 - p_mine)*1 + p_mine*(-10)
        elif act_type == "flag":
            # Flagging does not immediately yield success, but prevents revealing a mine by mistake later.
            # We give a small neutral reward.
            return 0.0

    def expectimax(self, board, depth):
        if depth == 0 or board.game_over or board.is_victory():
            # Terminal state or depth limit
            return 0.0, None

        actions = self.available_actions(board)
        if not actions:
            return 0.0, None

        best_value = -float('inf')
        best_action = None

        for action in actions:
            # Simulate action deterministically (flag action is deterministic)
            if action[0] == "flag":
                new_board = self.simulate_action(board, action)
                value, _ = self.expectimax(new_board, depth-1)
                # Immediate reward + future value
                total_value = self.action_reward(board, action) + value
                if total_value > best_value:
                    best_value = total_value
                    best_action = action
            else:
                # "reveal" is stochastic from the perspective of hitting a mine or not, but it is already included the expected reward in action_reward.
                # Since action_reward is already an expectation, it can be treated as deterministic here.
                new_board = self.simulate_action(board, action)
                # If we hit a mine, game_over will be True, but we've accounted for that in the reward.
                value, _ = self.expectimax(new_board, depth-1)
                total_value = self.action_reward(board, action) + value
                if total_value > best_value:
                    best_value = total_value
                    best_action = action

        return best_value, best_action

    def find_best_action(self):
        _, action = self.expectimax(self.initial_board, self.depth)
        return action

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
            actions.append(("flag", c.x, c.y))
        return actions

    def simulate_action(self, board, action):
        # Return a copy of the board after the action is applied
        new_board = copy.deepcopy(board)
        act_type, x, y = action
        if act_type == "reveal":
            new_board.reveal_cell(x, y)
            if new_board.grid[y][x].has_mine:
                new_board.game_over = True
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
            return (1 - p_mine) * 1 + p_mine * (-10)
        elif act_type == "flag":
            # Reward for flagging: reduce risk, enhance clarity
            return 0.5 if p_mine > 0.7 else 0.0

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
            act_type, x, y = action
            if act_type == "reveal":
                p_mine = self.probabilities.get((x, y), 0.5)

                # Handle stochastic outcomes for "reveal"
                # Simulate safe reveal
                safe_board = self.simulate_action(board, action)
                safe_board.grid[y][x].has_mine = False
                safe_value, _ = self.expectimax(safe_board, depth - 1)

                # Simulate mine hit
                mine_board = self.simulate_action(board, action)
                mine_board.grid[y][x].has_mine = True
                mine_board.game_over = True
                mine_value = -10  # Immediate loss value

                # Expected value
                total_value = (1 - p_mine) * (self.action_reward(board, action) + safe_value) + p_mine * mine_value
            else:
                # "flag" is deterministic
                new_board = self.simulate_action(board, action)
                value, _ = self.expectimax(new_board, depth - 1)
                total_value = self.action_reward(board, action) + value

            if total_value > best_value:
                best_value = total_value
                best_action = action

        return best_value, best_action

    def update_probabilities(self, board):
        # Dynamic update of probabilities based on the current board state
        for y in range(board.height):
            for x in range(board.width):
                cell = board.grid[y][x]
                if not cell.revealed and not cell.flagged:
                    neighbors = board.get_neighbors(x, y)
                    revealed_neighbors = [n for n in neighbors if n.revealed]

                    if revealed_neighbors:
                        clue_mines = sum(n.neighbor_mines for n in revealed_neighbors)
                        clue_flags = sum(1 for n in neighbors if n.flagged)
                        self.probabilities[(x, y)] = max(0.0, (clue_mines - clue_flags) / len(neighbors))
                    else:
                        self.probabilities[(x, y)] = 0.5

    def find_best_action(self):
        self.update_probabilities(self.initial_board)
        _, action = self.expectimax(self.initial_board, self.depth)
        return action

    def print_probabilities(self):
        # Print the probabilities for debugging
        for y in range(self.initial_board.height):
            row = []
            for x in range(self.initial_board.width):
                row.append(f"{self.probabilities.get((x, y), 0.5):.2f}")
            print(" | ".join(row))

# Enhancements added:
# - Updated probabilities dynamically based on revealed clues and neighbors.
# - Handled stochastic outcomes for "reveal" in expectimax.
# - Introduced debugging tools to print probabilities.
# - Refined flagging reward based on mine likelihood.

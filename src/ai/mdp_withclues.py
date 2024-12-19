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
        # Generate all possible actions based on unrevealed cells
        actions = []
        for c in board.get_unrevealed_cells():
            actions.append(("reveal", c.x, c.y))
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
        """
        Reward based on probabilities and clues.
        - Revealing a safe cell: Positive reward (e.g., 1).
        - Revealing a mine: Negative reward (e.g., -10).
        - Revealing a clue cell: Higher reward proportional to its usefulness.
        - Flagging: Small neutral reward (strategic action).
        """
        act_type, x, y = action
        p_mine = self.probabilities.get((x, y), 0.5)
        cell = board.grid[y][x]

        if act_type == "reveal":
            if cell.revealed:  # Already revealed, no additional reward
                return 0.0
            # If the cell is a clue, add extra reward based on its value
            if not cell.has_mine and cell.neighbor_mines > 0:
                clue_value = cell.neighbor_mines
                return (1 - p_mine) * (1 + clue_value) + p_mine * (-10)
            # Safe cell or empty cell
            return (1 - p_mine) * 1 + p_mine * (-10)
        elif act_type == "flag":
            # Flagging action prevents a mine from being revealed
            # Small reward for strategic advantage
            return 0.1

    def expectimax(self, board, depth):
        """
        Expectimax algorithm with probabilistic consideration of mines and clues.
        - Handles the stochastic nature of Minesweeper (e.g., revealing cells with probabilities).
        """
        if depth == 0 or board.game_over or board.is_victory():
            return 0.0, None

        actions = self.available_actions(board)
        if not actions:
            return 0.0, None

        best_value = -float('inf')
        best_action = None

        for action in actions:
            # Simulate the action
            new_board = self.simulate_action(board, action)

            if action[0] == "flag":
                # Flag action is deterministic
                value, _ = self.expectimax(new_board, depth - 1)
                total_value = self.action_reward(board, action) + value
            else:  # Reveal action
                # "reveal" incorporates stochastic outcomes via probabilities
                value, _ = self.expectimax(new_board, depth - 1)
                total_value = self.action_reward(board, action) + value

            if total_value > best_value:
                best_value = total_value
                best_action = action

        return best_value, best_action

    def find_best_action(self):
        """
        Find the best action using the Expectimax algorithm.
        Returns:
            tuple: The best action as (action_type, x, y).
        """
        _, action = self.expectimax(self.initial_board, self.depth)
        return action

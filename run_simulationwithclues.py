from src.game.board_withclues import Board
from src.game.game_manager_2 import GameManager
from src.ai.bayesian_withclue import BayesianAnalyzer
from src.ai.mdp_withclues import MDP
from src.metrics.dynamic_gr import DynamicGR
from src.utils.logger import CSVLogger

def run_single_game(width=9, height=9, mines=10, max_steps=200):
    # Initialize game components
    board = Board(width, height, mines)
    gm = GameManager(board)
    bayes = BayesianAnalyzer()
    gr = DynamicGR()
    logger = CSVLogger("gr_metrics.csv")

    step = 0
    while not gm.is_over() and step < max_steps:
        # Compute probabilities for each cell
        probabilities = bayes.compute_probabilities(board)
        # bayes.print_probability_matrix()

        # Incorporate clues into decision-making
        # Update probabilities to favor cells with useful clues
        for cell in board.get_unrevealed_cells():
            clue_score = 0
            if not cell.revealed and cell.neighbor_mines > 0:
                clue_score = cell.neighbor_mines
            # Adjust probabilities slightly based on clue score
            probabilities[(cell.x, cell.y)] *= (1 + 0.1 * clue_score)

        # Find the best action using the MDP
        mdp = MDP(board, probabilities, depth=2)
        action = mdp.find_best_action()

        if action is None:
            # No action available, terminate
            break

        act_type, x, y = action
        gm.make_move(x, y, act_type)

        # Update and log GR metrics
        gr_value, gr_data = gr.update(board, step, probabilities)
        logger.log(step, gr_data)

        step += 1

    return gm.is_victory()

if __name__ == "__main__":
    # Run multiple simulations and print the success rate
    num_games = 20
    wins = 0
    for i in range(num_games):
        result = run_single_game(9, 9, 10)
        if result:
            wins += 1
        print(f"Game {i+1}/{num_games}: {'Win' if result else 'Lose'}")

    print(f"Win rate: {wins}/{num_games}")

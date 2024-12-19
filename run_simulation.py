from src.game.board import Board
from src.game.game_manager import GameManager
from src.ai.bayesian_sj_2 import BayesianAnalyzer
from src.ai.mdp import MDP
from src.metrics.dynamic_gr import DynamicGR
from src.utils.logger import CSVLogger

def run_single_game(width=9, height=9, mines=10, max_steps=200):
    board = Board(width, height, mines)
    gm = GameManager(board)
    bayes = BayesianAnalyzer()
    gr = DynamicGR()
    logger = CSVLogger("gr_metrics.csv")

    step = 0
    while not gm.is_over() and step < max_steps:
        probabilities = bayes.compute_probabilities(board)
        bayes.print_probability_matrix()
        mdp = MDP(board, probabilities, depth=2)
        action = mdp.find_best_action()

        if action is None:
            # No action found
            break

        act_type, x, y = action
        gm.make_move(x, y, act_type)

        gr_value, gr_data = gr.update(board, step, probabilities)
        logger.log(step, gr_data)

        step += 1

    return gm.is_victory()

if __name__ == "__main__":
    # Run multiple simulations and print success rate
    num_games = 5
    wins = 0
    for i in range(num_games):
        result = run_single_game(9,9,10)
        if result:
            wins += 1
        print(f"Game {i+1}/{num_games}: {'Win' if result else 'Lose'}")

    print(f"Win rate: {wins}/{num_games}")

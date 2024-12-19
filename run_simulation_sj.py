from src.game.board_sj import Board
from src.game.game_manager_sj import GameManager
from src.ai.bayesian_sj_3 import BayesianAnalyzer
from src.ai.mdp_sj import MDP
from src.metrics.dynamic_gr_sj import DynamicGR
from src.utils.logger import CSVLogger

def run_single_game(width=9, height=9, mines=10, max_steps=200, log_file="gr_metrics.csv"):
    board = Board(width, height, mines)
    gm = GameManager(board)
    bayes = BayesianAnalyzer()
    gr = DynamicGR(log_file=log_file)

    step = 0
    while not gm.is_over() and step < max_steps:
        try:
            probabilities = bayes.compute_probabilities(board)
            bayes.print_probability_matrix()
            mdp = MDP(board, probabilities, depth=2)
            action = mdp.find_best_action()

            if action is None:
                print("No valid action found. Ending game.")
                break

            act_type, x, y = action
            gm.make_move(x, y, act_type)

            gr_value, gr_data = gr.update(board, step, probabilities)
            step += 1
        except Exception as e:
            print(f"Error during game execution: {e}")
            break

    # Optional: Visualize GR trends
    gr.visualize_gr_history()

    return gm.is_victory()

def run_multiple_games(num_games=5, width=9, height=9, mines=10, max_steps=200):
    wins = 0
    logger = CSVLogger("game_results.csv")

    for i in range(num_games):
        print(f"Starting Game {i + 1}/{num_games}")
        result = run_single_game(width, height, mines, max_steps, log_file=f"game_{i + 1}_metrics.csv")
        wins += int(result)
        logger.log(i + 1, {"step": "-", "gr": "-", "complexity": "-", "goal_progress": "-", "entropy": "-", "acceleration": "-", "jerk": "-", "result": "Win" if result else "Lose"})

        print(f"Game {i + 1}/{num_games}: {'Win' if result else 'Lose'}")

    print(f"Win rate: {wins}/{num_games} ({(wins / num_games) * 100:.2f}%)")

if __name__ == "__main__":
    run_multiple_games(num_games=5)

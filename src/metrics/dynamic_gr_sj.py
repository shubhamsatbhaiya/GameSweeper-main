import math
import csv
import matplotlib.pyplot as plt

class DynamicGR:
    def __init__(self, log_file=None):
        self.history = []
        self.reveals_history = []
        self.logger = CSVLogger(log_file) if log_file else None

    def update(self, board, step, probabilities):
        unrevealed = board.get_unrevealed_cells()
        total_cells = board.width * board.height

        # Handle edge case: Empty board
        if total_cells == 0:
            complexity = 0.0
        else:
            complexity = len(unrevealed) / total_cells

        safe_cells = total_cells - board.mines
        revealed_safe = sum(1 for row in board.grid for c in row if c.revealed and not c.has_mine)

        # Handle edge case: No safe cells
        if safe_cells == 0:
            goal_progress = 0.0
        else:
            goal_progress = revealed_safe / safe_cells

        # Compute entropy from probabilities: For each unrevealed cell, p = probability of mine
        entropy = 0.0
        for c in unrevealed:
            p = probabilities.get((c.x, c.y), 0.5)
            if 0 < p < 1:  # Avoid log2 errors for p=0 or p=1
                entropy += -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

        # Psychological metrics: acceleration & jerk
        self.reveals_history.append(revealed_safe)
        acc, jerk = self._compute_psychological_metrics()

        # Refined GR calculation:
        base_gr = math.sqrt(goal_progress * (1 - complexity + 1e-9))  # Add small epsilon to avoid division issues

        # Add entropy factor to indicate uncertainty
        entropy_weight = 0.1  # Adjustable parameter for tuning entropy impact
        dynamic_factor = 1 + (entropy * entropy_weight)

        # Add motion factor based on acceleration and jerk
        acc_weight = 0.01  # Adjustable parameter for tuning acceleration impact
        jerk_weight = 0.001  # Adjustable parameter for tuning jerk impact
        motion_factor = (1 + abs(acc) * acc_weight + abs(jerk) * jerk_weight)

        # Normalize GR value
        gr_value = (base_gr * dynamic_factor * motion_factor) / (1 + entropy_weight + acc_weight + jerk_weight)

        data_point = {
            'step': step,
            'gr': gr_value,
            'complexity': complexity,
            'goal_progress': goal_progress,
            'entropy': entropy,
            'acceleration': acc,
            'jerk': jerk
        }
        self.history.append(data_point)

        # Log data to CSV if logger is enabled
        if self.logger:
            self.logger.log(step, data_point)

        return gr_value, data_point

    def _compute_psychological_metrics(self):
        if len(self.reveals_history) < 3:
            return 0.0, 0.0

        # Calculate acceleration and jerk
        acc = self.reveals_history[-1] - self.reveals_history[-2]
        prev_acc = self.reveals_history[-2] - self.reveals_history[-3]
        jerk = acc - prev_acc
        return acc, jerk

    def visualize_gr_history(self):
        # Optional: Provide a simple way to visualize GR trends
        try:
            
            steps = [data['step'] for data in self.history]
            gr_values = [data['gr'] for data in self.history]

            plt.plot(steps, gr_values, marker='o', label='GR Value')
            plt.xlabel('Step')
            plt.ylabel('GR Value')
            plt.title('GR Value Over Time')
            plt.legend()
            plt.show()
        except ImportError:
            print("Visualization requires matplotlib. Install it to use this feature.")

    def get_history(self):
        # Retrieve the history of GR calculations
        return self.history

class CSVLogger:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "GR", "Complexity", "Goal_Progress", "Entropy", "Acceleration", "Jerk"])

    def log(self, step, gr_data):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([step, gr_data['gr'], gr_data['complexity'], gr_data['goal_progress'],
                             gr_data['entropy'], gr_data['acceleration'], gr_data['jerk']])

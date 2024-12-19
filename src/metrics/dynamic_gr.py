import math

class DynamicGR:
    def __init__(self):
        self.history = []
        self.reveals_history = []

    def update(self, board, step, probabilities):
        unrevealed = board.get_unrevealed_cells()
        total_cells = board.width * board.height
        complexity = len(unrevealed) / total_cells if total_cells > 0 else 0.0

        safe_cells = total_cells - board.mines
        revealed_safe = sum(1 for row in board.grid for c in row if c.revealed and not c.has_mine)
        goal_progress = revealed_safe / safe_cells if safe_cells > 0 else 0

        # Compute entropy from probabilities: For each unrevealed cell, p = probability of mine
        # Entropy for that cell: H_cell = -(p*log2(p) + (1-p)*log2(1-p)) if p not in {0,1}
        entropy = 0.0
        for c in unrevealed:
            p = probabilities.get((c.x, c.y), 0.5)
            if p > 0 and p < 1:
                entropy += -(p*math.log2(p) + (1-p)*math.log2(1-p))

        # Psychological metrics: acceleration & jerk
        self.reveals_history.append(revealed_safe)
        acc, jerk = self._compute_psychological_metrics()

        # Refined GR calculation:
        # Base GR: sqrt(goal_progress * (1 - complexity))
        base_gr = math.sqrt(goal_progress * (1 - complexity + 1e-9))
        # Increase complexity stability: add a small epsilon

        # Add entropy factor to indicate uncertainty
        dynamic_factor = 1 + (entropy * 0.1)

        # Add motion factor based on acceleration and jerk
        motion_factor = (1 + abs(acc)*0.01 + abs(jerk)*0.001)

        gr_value = base_gr * dynamic_factor * motion_factor

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
        return gr_value, data_point

    def _compute_psychological_metrics(self):
        if len(self.reveals_history) < 3:
            return 0.0, 0.0
        # acceleration = delta in reveals
        acc = self.reveals_history[-1] - self.reveals_history[-2]
        prev_acc = self.reveals_history[-2] - self.reveals_history[-3]
        jerk = acc - prev_acc
        return acc, jerk

import csv

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

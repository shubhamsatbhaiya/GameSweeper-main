class GameManager:
    def __init__(self, board):
        self.board = board

    def make_move(self, x, y, action="reveal"):
        """
        action: "reveal" or "flag"
        """
        if self.board.game_over:
            return

        if action == "reveal":
            self.board.reveal_cell(x, y)
        elif action == "flag":
            self.board.flag_cell(x, y)

    def is_over(self):
        return self.board.game_over or self.board.is_victory()

    def is_victory(self):
        return self.board.is_victory()

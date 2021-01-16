class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def check_win(self, winning_score):
        if self.score == winning_score:
            return True
        else:
            return False

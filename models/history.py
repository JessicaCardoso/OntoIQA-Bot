from .turn import Turn


class History:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.bot_id = kwargs.get("bot_id")
        self.turns = []

    def add_turn(self, turn: Turn):
        self.turns.append(turn)

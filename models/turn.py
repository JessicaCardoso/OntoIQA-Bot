from pandas import DataFrame


class Turn:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.message_id = kwargs.get("message_id")
        self.user_text = kwargs.get("user_text")
        self.bot_text = kwargs.get("bot_answer")
        self.answer_confidence = kwargs.get("answer_confidence")
        self.suggestions = kwargs.get("suggestions")
        self.results = None

    def set_bot_answer(
        self, text: str, results: DataFrame, suggestions: list = []
    ):
        self.bot_text = text
        self.results = results
        self.suggestions = suggestions

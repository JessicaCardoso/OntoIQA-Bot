import pandas as pd
import random
import requests
import requests_cache
import re
import os
from requests.exceptions import ConnectionError, RequestException

from .ontoexplorer import Recommendation

# requests_cache.install_cache(
#     "data/iqa_cache", backend="sqlite", expire_after=300
# )


class InterfaceIQA:
    def __init__(self, use_rec=False):
        self.use_rec = use_rec
        if use_rec:
            print("Recommendation activated!")
            self._recommendation = Recommendation()

    def preprocess(self, text):
        matches = re.match(r"💡 (.*): (.*)", text, re.M | re.I)
        if matches:
            return matches.group(2)
        matches = re.match(r"💡 Mostre-me (.*).", text, re.M | re.I)
        if matches:
            return matches.group(1)
        return text

    def get_answer_from_iqa(self, query, uid, hid, bid):
        query = self.preprocess(query)
        try:
            r = requests.get(
                os.getenv("IQA_URL"),
                params={"q": query, "uid": uid, "hid": hid, "bid": bid},
            )
            if r.status_code != 200:
                raise ConnectionError
            else:
                response_dict = r.json()
                response_dict["results"] = [
                    pd.DataFrame(r) for r in response_dict["results"]
                ]
        except ConnectionError as e:
            print(e)
            response_dict = {
                "text": "Desculpe-me, ocorreu um erro com a conexão, por favor, tente mais tarde, se o erro persistir contate-me pelo @JessicaContatoBot.",
                "results": [],
                "eval_options": False,
                "relations": [],
                "related": [],
                "suggestion_text": "",
                "success": False,
                "details": {},
            }
        return response_dict

    def get_answer(self, text, user_id, history_id, bot_id):
        response = self.get_answer_from_iqa(text, user_id, history_id, bot_id)
        if response["relations"] and not response["related"]:
            # print(response["relations"])
            if self.use_rec:
                (
                    response["suggestion_text"],
                    response["related"],
                ) = self._recommendation.get_recommendations(
                    response["relations"]
                )
        return response

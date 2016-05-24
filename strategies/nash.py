from strategy_base import StrategyBase
import sys
import random

__author__ = 'Hector Azpurua'


class Nash(StrategyBase):
    def __init__(self):
        self.strategy_name = 'Nash'
        self.probabilities = {
            "Skynet": float(0.56),
            "Xelnaga": float(0.254),
            "NUSBot": float(0.186)
        }
        self.bot_list = ["Skynet", "Xelnaga", "NUSBot"]
        self.result_list = []
        self.match_list = []
        self.s_id = None
        pass

    def get_name(self):
        return self.strategy_name

    def set_id(self, s_id):
        self.s_id = s_id
        pass

    def set_match_list(self, match_list):
        self.match_list = match_list
        pass

    def set_result_list(self, result_list):
        self.result_list = result_list

    def get_next_bot(self):
        prob = 0
        for key in self.probabilities.keys():
            prob += self.probabilities[key]

        if prob != 1:
            print >> sys.stderr, "Sum of probabilities is not 1"
            return None

        rand_n = random.uniform(0, 1)

        prob = 0
        for key in self.probabilities.keys():
            prob += self.probabilities[key]
            if rand_n < prob:
                return key

        print >> sys.stderr, 'Something estrange happened, a bot wasn\'t selected by Nash eq'
        return None

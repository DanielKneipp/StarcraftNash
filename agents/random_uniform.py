from agent_base import AgentBase
import random

__author__ = 'Hector Azpurua'


class RandomUniform(AgentBase):
    """
    Select a random strategy
    """

    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        #self.bot_list = ["Skynet", "Xelnaga", "NUSBot"]
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
        bot = random.choice(self.bot_list)
        return bot

    def ranking(self):
        """
        Returns the most frequent choice by the opponent
        :return:
        """
        return {bot: 1.0/len(self.bot_list) for bot in self.bot_list}


from agent_base import AgentBase
import random_uniform

__author__ = 'Hector Azpurua'


class Unique(AgentBase):
    """
    Selects the same strategy every time
    """

    def __init__(self, strategy_name):
        AgentBase.__init__(self, strategy_name)
        # self.result_list = []
        # self.match_list = []
        # self.s_id = None
        # pass

    def get_next_bot(self):
        """
        Always returns the same bot (configured in __init__)
        :return:
        """
        return self.strategy_name

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return:
        """
        # TODO - change this bot list that was manually made for the
        # actual list on the database
        bots = ["Xelnaga", "CruzBot", "NUSBot", "Aiur", "Skynet"]
        
        #Creates ranking list
        ranking = []
        for bot_name in bots:   
            if bot_name == self.get_name():
                value = (bot_name, 1)
            else:
                value = (bot_name, 0)
            
            ranking.append(value)


        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)

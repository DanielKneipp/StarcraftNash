from agent_base import AgentBase

__author__ = 'Anderson Tavares'


class Rotate(AgentBase):
    """
    Selects the next bot in the list each time
    """

    def __init__(self, strategy_name):
        AgentBase.__init__(self, strategy_name)
        # self.result_list = []
        # self.match_list = []
        # self.s_id = None
        pass

    def get_next_bot(self):
        """
        Returns the next bot in the list
        :return:
        """
        return self.bot_list[len(self.match_list) % len(self.bot_list)]

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """

        ranking = []

        for bot in self.bot_list:
            if bot == self.bot_list[len(self.match_list) % len(self.bot_list)]:
                ranking.append((bot, 1))
            else:
                ranking.append((bot, 0))


        # returns the sorted list
        return ranking

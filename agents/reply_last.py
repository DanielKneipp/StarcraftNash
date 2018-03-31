from agent_base import AgentBase
from config import Config
import scorechart
import random

__author__ = 'Anderson Tavares'


class PriorKnowledgeReplyLast(AgentBase):
    """
    Selects the bot that would beat last opponent choice, querying a score chart
    previously computed
    """

    def __init__(self, strategy_name):
        AgentBase.__init__(self, strategy_name)

        # loads score chart from file
        self.score_chart = scorechart.from_file(
            Config.get_instance().get(Config.SCORECHART_FILE),
            self.bot_list
        )

    def get_next_bot(self):

        # finds opponent's last choice
        opponent_choice = self.opponent_choice(-1)

        # no history present or could not count victories, chooses randomly
        if opponent_choice is None:
            return random.choice(self.bot_list)

        # responds with opponent's nemesis, i.e the one that makes it perform worst
        return min(self.score_chart[opponent_choice], key=self.score_chart[opponent_choice].get)

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """
        #create temporary dict
        ranking = {choice: 0 for choice in self.bot_list}
        ranking[self.get_next_bot()] = 1 #change value of the next choice

        #create list of tuples from the dict
        ranking = [(choice, value) for choice, value in ranking.iteritems()]

        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)

class NoPriorReplyLast(AgentBase):
    """
    Selects the bot that won most matches against last opponent choice
    """

    def __init__(self, strategy_name):
        AgentBase.__init__(self, strategy_name)
        self.result_list = []
        self.match_list = []
        self.s_id = None
        pass

    def get_next_bot(self):
        # usage: win_count[strategy1][strategy2]
        win_count = self.calculate_score_table() #TODO do this incrementally!

        # finds opponent's last choice
        opponent_choice = self.opponent_choice(-1)

        # no history present or could not count victories, chooses randomly
        if opponent_choice is None:
            return random.choice(self.bot_list)

        # responds with opponent's nemesis, i.e the one that makes it perform worst
        return min(win_count[opponent_choice], key=win_count[opponent_choice].get)

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """
        #create temporary dict
        ranking = {choice: 0 for choice in self.bot_list}
        ranking[self.get_next_bot()] = 1 #change value of the next choice

        #create list of tuples from the dict
        ranking = [(choice, value) for choice, value in ranking.iteritems()]

        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)

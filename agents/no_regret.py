from agent_base import AgentBase
from config import Config
import random
import scorechart

__author__ = 'Barbara Lopes'


class NoRegret(AgentBase):
    def __init__(self, strategy_name):
        AgentBase.__init__(self, strategy_name)

        self.result_list = []
        self.match_list = []
        
        config = Config.get_instance()
        
        # read score chart from a file
        self.score_chart = scorechart.from_file(
            config.get(Config.SCORECHART_FILE),
            self.bot_list
        )
        
        # get weights
        self.regrets = config.get(Config.INITIAL_REGRETS)
        
    def get_next_bot(self):
        # finds opponent's last choice
        opponent_choice = self.opponent_choice(-1)

        # no history present or could not count victories, chooses randomly
        if opponent_choice is None:
            return random.choice(self.bot_list)
        
        my_choice = self.my_choice(-1)
        
        actual_payoff = self.match_result(-1)
        
        payoffs = {bot: 0.0 for bot in self.bot_list}
        
        scores = self.score_chart[opponent_choice]
        
        for bot in self.bot_list:
            payoffs[bot] = scores[bot]/100.0
         
        payoffs[my_choice] = 0.0    
        
        for bot in self.regrets:
            self.regrets[bot] += payoffs[bot] - (actual_payoff)

        response = self.get_weighted_choice(self.regrets.copy())
        
        return response        
    
    def get_weighted_choice(self, choices):     
        total = sum(choices[choice] for choice in choices)
        r = random.uniform(0, total)
        upto = 0
        
        weights = {choices[bot] for bot in choices}
        min_weight = min(weights)

        for choice in choices:
            
            probability = choices[choice] # to get only positive weights
            if min_weight < 0:
                probability += abs(min_weight)
                
            if upto + probability >= r:
                return choice
            upto += probability
        assert False, "Shouldn't get here"  
        
    def set_match_list(self, match_list):
        self.match_list = match_list

    def set_result_list(self, result_list):
        self.result_list = result_list

    def set_id(self, s_id):
        self.s_id = s_id
    
    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """
        # constructs a list of tuples from the dict
        ranking = [(choice, score * -1) for choice, score in self.regrets.iteritems()]

        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)

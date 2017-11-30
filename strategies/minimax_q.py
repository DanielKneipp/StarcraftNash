import random
import numpy as np
from collections import OrderedDict
import nash
from strategy_base import StrategyBase
from config import Config

class MiniMaxQ(StrategyBase):

    MINIMAXQ_ALPHA_TAG = 'alpha'

    def __init__(self, strategy_name, config_name):
        super(MiniMaxQ, self).__init__(strategy_name)

        config = Config.get_instance()

        if config_name is None:
            raise Exception('Fictitious Play must have a configuration specified at the initialization time')

        self.set_config_name(config_name)

        # set counters
        # Note: self.bot_list can't be used here because it isn't initialized from the config file yet
        bots = config.get_bots().keys()
        self.q_matrix = OrderedDict({bot: 0 for bot in bots})
        self.q_matrix = OrderedDict({bot: self.q_matrix.copy() for bot in bots})

        # Set alpha
        if self.MINIMAXQ_ALPHA_TAG in config.get(self.config_name):
            self.alpha = config.get(self.config_name)[self.MINIMAXQ_ALPHA_TAG]
        else:
            self.alpha = 0.3

    def get_next_bot(self):
        self.update_qmatrix()
        return self.nash_choice()

    def nash_choice(self):
        # Use the ordered bots list
        bots = self.q_matrix.keys()
        nash_eq = self.calc_nasheq(self.q_matrix)
        if nash_eq is None:
            return self.get_choice_top_vals()
        else:
            return np.random.choice(bots, 1, p=nash_eq)[0]

    def calc_nasheq(self, qmatrix):
        mat = np.array([v.values() for k, v in qmatrix.iteritems()])
        game = nash.Game(mat)
        try:
            return list(game.support_enumeration())[0][0]
        except IndexError:
            return None

    def update_qmatrix(self):
        # finds opponent's last choice
        opponent_choice = self.opponent_choice(-1)
        # Get my past choice
        my_past_choice = self.my_choice(-1)
        # Past result
        past_result = None
        if self.history_length() > 0:
            past_result = self.match_result(self.history_length() - 1)

        # Update q-matrix
        if opponent_choice is not None and my_past_choice is not None:
            q = self.q_matrix[my_past_choice][opponent_choice]
            self.q_matrix[my_past_choice][opponent_choice] += self.alpha * (past_result - q)

    def get_choice_top_vals(self):
        # Get the lines (choices) with highest values
        sums = {choice: sum(d.values()) for choice, d in self.q_matrix.iteritems()}
        max_sums = max(sums.values())
        possible_choices = [choice for choice, val in sums.iteritems() if val == max_sums]

        response = random.choice(possible_choices)
        return response

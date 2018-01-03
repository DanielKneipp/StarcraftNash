from agent_base import AgentBase
from config import Config
import scorechart
import random

__author__ = 'Daniel Kneipp'


class FictitiousPlay(AgentBase):

    STOCHASTIC_TAG = "be-stochastic"

    def __init__(self, strategy_name, config_name):
        super(FictitiousPlay, self).__init__(strategy_name)

        config = Config.get_instance()

        if config_name is None:
            raise Exception('Fictitious Play must have a configuration specified at the initialization time')

        self.set_config_name(config_name)

        # read score chart from a file
        self.score_chart = scorechart.from_file(
            config.get(Config.SCORECHART_FILE),
            self.bot_list
        )

        # get weights
        self.initial_weights = config.get(self.config_name)[Config.FICTITIOUS_INITIAL_WEIGHTS]
        self.running_weights = config.get(self.config_name)[Config.FICTITIOUS_RUNNING_WEIGHTS]

        # set counters
        # Note: self.bot_list can't be used here because it isn't initialized from the config file yet
        bots = config.get_bots()
        self.opponent_choice_counter = {choice_name: self.initial_weights[choice_name] for choice_name in
                                        bots}
        self.count_sum = sum([x for _, x in self.opponent_choice_counter.items()])

        # set config og stochastic feature. Default value is True
        if self.STOCHASTIC_TAG in config.get(self.config_name):
            self.be_stochastic = config.get(self.config_name)[self.STOCHASTIC_TAG]
        else:
            self.be_stochastic = True

    def get_next_bot(self):
        # finds opponent's last choice
        opponent_choice = self.opponent_choice(-1)

        # if there is a history of opponent's choices
        if opponent_choice is not None:
            # update counter
            self.opponent_choice_counter[opponent_choice] += self.running_weights[opponent_choice]
            self.count_sum += self.running_weights[opponent_choice]

        # update beliefs
        opponent_choice_beliefs = [(k, v/self.count_sum) for k, v in self.opponent_choice_counter.items()]

        # retrieve the most chosen bot
        if self.be_stochastic:
            likely_opponent_bot_with_prob = max(opponent_choice_beliefs, key=lambda belief: belief[1])
            likely_opponent_bot_list = [b[0] for b in opponent_choice_beliefs if b[1] == likely_opponent_bot_with_prob[1]]
            likely_opponent_bot = random.choice(likely_opponent_bot_list)
        else:
            likely_opponent_bot = max(opponent_choice_beliefs, key=lambda belief: belief[1])[0]

        # dict representation of the opponent_choice_beliefs
        blf_dict = {d[0]: d[1] for d in opponent_choice_beliefs}

        # calculate the expected utilities
        evs = {k: 0 for k in blf_dict}
        for s1 in evs:
            for s2 in evs:
                evs[s1] = evs[s1] + self.score_chart[s1][s2] * blf_dict[s2]

        response = max(evs, key=evs.get)
        return response

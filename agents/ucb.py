from agent_base import AgentBase
from config import Config
from math import log, sqrt
from sys import maxint
from sys import stdout

__author__ = 'Anderson'


class UCB1(AgentBase):
    """
    Use the UCB1 method for strategy selection:
    Chooses the option with highest average value + upper confidence bound of
    estimation uncertainty
    Reference: Auer, Cesa-Bianchi, Fischer. Finite-time Analysis of the
    Multiarmed Bandit Problem. Machine Learning (2002).
    """

    def __init__(self, strategy_name):
        """
        Initializes UCB1 strategy selection method
        """

        AgentBase.__init__(self, strategy_name)
        self.formula = self.ucb1

        # overrides bot_list with bandit choices
        self.bot_list = Config.get_instance().get_bandit_choices()

        self.data = {choice: {'trials': 0, 'sum': 0, 'sum_of_squares': 0} for choice in self.bot_list}

    def prepare(self):
        """
        Erases statistics
        :return:
        """
        self.data = {choice: {'trials': 0, 'sum': 0, 'sum_of_squares': 0} for choice in self.bot_list}

    def update(self):
        """
        Updates statistics based on previous match result
        :return: dict
        """
        '''if self.my_choice(-1) is not None:  # skips in 1st match
            my_choice = self.my_choice(-1)
            self.data[my_choice]['sum'] += self.match_result(-1)
            self.data[my_choice]['sum_of_squares'] += self.match_result(-1) ** 2
            self.data[my_choice]['trials'] += 1'''

        data = {choice: {'trials': 0, 'sum': 0, 'sum_of_squares': 0} for choice in self.bot_list}

        # count scores and selects greedily
        for match in range(self.history_length()):
            my_choice = self.my_choice(match)
            data[my_choice]['sum'] += self.match_result(match)
            data[my_choice]['sum_of_squares'] += self.match_result(match) ** 2
            data[my_choice]['trials'] += 1

        return data

    def get_next_bot(self):
        """
        Chooses the option with highest average value + upper confidence bound of
        estimation uncertainty
        :return: str
        """

        data = self.update()  # TODO: do this incrementally

        #self.update()  # updates stats from last match result

        best_strategy = max(data, key=lambda x: self.formula(data[x]))
        return best_strategy

    def ucb1(self, choice):
        """
        Returns the Upper Confidence Bound of an option using the UCB1 formula
        UCB1 formula is: average_reward + sqrt(2 * ln(total_num_of_trials) / num_trials)
        Where total_num_of_trials is the number of matches played so far.
        :param choice: dict with sum, sum_of_squares and trials, the option to have its score calculated
        :return:float
        """
        if choice['trials'] == 0:
            return maxint

        stdout.write('\rhistory: %d, trials: %d    ' % (self.history_length(), choice['trials']))

        return float(choice['sum'])/choice['trials'] + sqrt(2*log(self.history_length()) / choice['trials'])

    def get_name(self):
        return self.strategy_name

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """
    
        data = self.update()
        ranking = []

        # constructs a list of tuples from the dict
        for bot_name, hist_data in data.items():
            
            #calculate the ranking value using the UCB1 formula
            if hist_data['trials'] == 0:
                ucb_value = maxint
            else:
                ucb_value = float(hist_data['sum'])/hist_data['trials'] + sqrt(2*log(self.history_length()) / hist_data['trials'])

            ranking.append((bot_name, ucb_value))


        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)

class UCB1Tuned(UCB1):
    """
    Uses the UCB1-tuned method for strategy selection:
    Reference: Auer, Cesa-Bianchi, Fischer. Finite-time Analysis of the
    Multiarmed Bandit Problem. Machine Learning (2002).
    """

    def __init__(self, strategy_name):
        """
        Initializes UCB1 strategy selection method
        """

        UCB1.__init__(self, strategy_name)
        self.formula = self.ucb1_tuned

    def ucb1_tuned(self, choice):
        """
        Returns the Upper Confidence Bound of an option using the UCB1-Tuned formula
        UCB1-Tuned formula is: average_reward + sqrt(min(1/4, Vj(nj)) * ln(total_num_of_trials) / num_trials)
        Where total_num_of_trials is the number of matches played so far.
        :param choice: dict with sum, sum_of_squares and trials
        :return:float
        """
        if choice['trials'] == 0:
            return maxint

        return float(choice['sum']) / choice['trials'] + self.variance_ucb(choice)

    def variance_ucb(self, choice):
        """
        Calculates the upper confidence bound for the variance of a choice.
        Uses the formula on page 245 of our reference (p. 11 on pdf)
        (Finite-time Analysis of the Multiarmed Bandit Problem)
        :param choice: dict with sum, sum_of_squares and trials
        :return: float
        """

        average_of_squares = float(choice['sum_of_squares']) / choice['trials']
        squared_average = (float(choice['sum']) / choice['trials']) ** 2

        return average_of_squares - squared_average + sqrt(2 * log(self.history_length()) / choice['trials'])

    def ranking(self):
        """
        Returns the sorted ranking of choices for next bot
        :return: list
        """
    
        data = self.update()
        ranking = []

        # constructs a list of tuples from the dict
        for bot_name, hist_data in data.items():
            
            #calculate the ranking value using the UCB1 formula
            value = self.ucb1_tuned(hist_data)
            
            ranking.append((bot_name, value))


        # returns the sorted list
        return sorted(ranking, key=lambda x: x[1], reverse=True)





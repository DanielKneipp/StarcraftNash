import random
import numpy as np
from collections import OrderedDict
from os import path, makedirs
import pickle
import string
import time
import copy
import nash
import scipy
from agent_base import AgentBase
from config import Config


def random_string(length, num_only=False):
    pool = string.digits
    if not num_only:
        pool += string.letters
    return ''.join(random.choice(pool) for i in xrange(length))


class MiniMaxQ(AgentBase):

    MINIMAXQ_ALPHA_TAG = 'alpha'

    def __init__(self, strategy_name, config_name):
        super(MiniMaxQ, self).__init__(strategy_name)

        self.q_matrix_list_to_dump = []
        self.hash_str = str(int(round(time.time() * 1000)))

        self.config = Config.get_instance()

        if config_name is None:
            raise Exception('MinimaxQ must have a configuration specified at initialization')

        self.set_config_name(config_name)

        # set counters
        # Note: self.bot_list can't be used here because it isn't initialized from the config file yet
        bots = self.config.get_bots().keys()
        self.q_matrix = OrderedDict({bot: 1 for bot in bots})
        self.q_matrix = OrderedDict({bot: self.q_matrix.copy() for bot in bots})

        # Set alpha
        if self.MINIMAXQ_ALPHA_TAG in self.config.get(self.config_name):
            self.alpha = self.config.get(self.config_name)[self.MINIMAXQ_ALPHA_TAG]
        else:
            self.alpha = 0.3

    def get_next_bot(self):
        self.update_qmatrix()

        choice = self.nash_choice()

        # If it is the last round, save the qmatrix
        # if self.history_length() == (self.config.data[Config.NUM_MATCHES] - 1):
            # self.save_qmatrix_str('qmatrix_info/last_qmatrix_' + self.hash_str + '.txt')
            # self.dump_qmatrices('qmatrix_info/nash_problematic_qmatrices_' + self.hash_str + '.pkl')

        return choice

    def nash_choice(self):
        # Use the ordered bots list
        bots = self.q_matrix.keys()
        nash_eq = self.calc_nasheq(self.q_matrix)
        if nash_eq is None:
            return self.get_choice_top_vals()
        else:
            try:
                return np.random.choice(bots, 1, p=nash_eq)[0]
            except ValueError:
                print "ERROR: probabilities don't add to 1 %s" % nash_eq
                print "Choosing randomly"
                return random.choice(bots)

    def calc_nasheq(self, qmatrix):
        mat = np.array([v.values() for k, v in qmatrix.iteritems()])
        game = nash.Game(mat)

        def solve_support(game, errf):
            try:
                return np.absolute(list(game.support_enumeration())[0][0].round(9))
            except IndexError as e:
                return errf(game, e)

        def solve_vertex(game, errf1, errf2):
            try:
                return np.absolute(list(game.vertex_enumeration())[0][0].round(9))
            except scipy.spatial.qhull.QhullError as e:
                return errf1(game, e)
            except IndexError as e:
                return errf2(game, e)

        def solve_lemke(game, errf1, errf2, errf3, errf4):
            try:
                s = np.absolute(list(game.lemke_howson(0))[0].round(9))
            except Exception as e:
                return errf4(game, e)
            if np.NaN in s:
                return errf1(game, ValueError('There is a NaN on the equilibria'))
            if all(i == 0 for i in s):
                return errf2(game, ValueError('All equilibria values are 0'))
            if len(qmatrix) != len(s):
                return errf3(game, ValueError('Number of equilibria value don\'t match with qmatrix size'))
            return s

        def mark_qmatrix_to_dump(game, e):
            self.q_matrix_list_to_dump.append(copy.deepcopy(qmatrix))
            return None

        # solve_support_prepared = lambda game, e: solve_support(game, mark_qmatrix_to_dump)
        solve_vertex_prepared = lambda game, e: solve_vertex(
            game, 
            mark_qmatrix_to_dump, 
            mark_qmatrix_to_dump
        )
        solve_lemke_prepared = lambda game, e: solve_lemke(
            game, 
            solve_vertex_prepared, 
            solve_vertex_prepared, 
            solve_vertex_prepared,
            solve_vertex_prepared
        )

        # return solve_vertex(game, solve_support_prepared, solve_support_prepared)
        return solve_support(game, solve_lemke_prepared)

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

    def save_qmatrix_str(self, filename):
        # Build the string, starting with the keys, then
        # add the values
        string = ''
        for k, _ in self.q_matrix.iteritems():
            string += str(k) + ';'
        string = string[:-1]

        for _, vs in self.q_matrix.iteritems():
            string += '\n'
            for _, v in vs.iteritems():
                string += str(v) + ';'
            string = string[:-1]
        
        # Creates the path if it doesn't exists
        filename = path.abspath(filename)
        filepath = path.dirname(filename)
        if not path.isdir(filepath):
            makedirs(filepath)

        # Dump the qmatrix
        with open(filename, 'w') as f:
            f.write(string)

    def dump_qmatrices(self, filename):
        # Creates the path if it doesn't exists
        filename = path.abspath(filename)
        filepath = path.dirname(filename)
        if not path.isdir(filepath):
            makedirs(filepath)

        # Dump the qmatrix
        with open(filename, 'wb') as f:
            pickle.dump(self.q_matrix_list_to_dump, f, pickle.HIGHEST_PROTOCOL)

import os
import xml.etree.ElementTree as ET
import math

__author__ = 'Anderson Tavares'


def default_parser(type_parser):
    return lambda element: type_parser(element.get('value'))


def str_to_bool(element):
    return element.get('value').lower() == 'true'


def fictitious_options_parser(element):
    ops = {x.get('name'): float(x.get('value')) for x in element}
    return ops


class Config(object):
    """
    Class that handles configurations of an experiment
    """

    instance = None
    default_bots = {"Skynet": .33, "Xelnaga": .33, "CruzBot": .33}
    bandit_choices = []

    # parameter names (also tag names in .xml)
    BOTS = 'bots'
    BANDIT_CHOICES = 'bandit-choices'
    PLAYERS = 'players'
    SCORECHART_FILE = 'scorechart-file'

    FICTITIOUS_INITIAL_WEIGHTS = 'fictitious-initial-weights'
    FICTITIOUS_RUNNING_WEIGHTS = 'fictitious-running-weights'
    E_GREEDY_EXPLORATION = 'egreedy-exploration'
    E_NASH_EXPLOITATION = 'enash-exploitation'
    EXP3_GAMMA = 'exp3-gamma'
    SHUFFLE_MATCH_LIST = 'shuffle-match-list'
    RANDOM_SEED = 'random-seed'
    REPETITIONS = 'repetitions'
    NUM_MATCHES = 'num-matches'
    MATCH_POOL_FILE = 'match-pool-file'
    ROUND_ROBIN = 'round-robin'
    OUTPUT_SPREADSHEET = 'output-spreadsheet'
    OUTPUT_INTERMEDIATE = 'output-intermediate'
    VERBOSE = 'verbose'
    PLOT = 'plot'

    # xml tag names
    CHOICES_FIELD = 'choices'
    PARAMETERS_FIELD = 'parameters'

    @staticmethod
    def get_instance():
        """
        Returns the (singleton) instance of Config object
        :return: Config
        """
        if Config.instance is None:
            Config.instance = Config()
        return Config.instance

    def __init__(self, ):
        # dir of config file needed coz' path to server is relative
        # self.cfgdir = os.path.dirname(os.path.realpath(cfgpath))

        # stores values of parameters (initialized with defaults)
        self.data = {
            self.BOTS: self.default_bots,                   # dict of choices (and their nash probabilities)
            self.BANDIT_CHOICES: self.default_bots.keys(),  # list of choices for bandit-based methods
            self.PLAYERS: [],                               # list of players
            self.FICTITIOUS_INITIAL_WEIGHTS: {bot: 1.0 / len(self.default_bots) for bot in self.default_bots},
            self.FICTITIOUS_RUNNING_WEIGHTS: {bot: 1.0 for bot in self.default_bots},
            self.E_GREEDY_EXPLORATION: .1,
            self.E_NASH_EXPLOITATION: .1,
            self.EXP3_GAMMA: .1,
            self.VERBOSE: True,
            self.SHUFFLE_MATCH_LIST: False,
            self.RANDOM_SEED: None,
            self.REPETITIONS: 1,
            self.NUM_MATCHES: 100,
            self.ROUND_ROBIN: True,
            self.SCORECHART_FILE: 'config/scorechart_fortress.csv',
            self.MATCH_POOL_FILE: 'results_demo/fortress1000.txt',
            self.OUTPUT_SPREADSHEET: None,
            self.OUTPUT_INTERMEDIATE: 'intermediate',
            self.PLOT: False,
        }

        # stores type conversions for parameters
        self.parser = {
            self.FICTITIOUS_INITIAL_WEIGHTS: fictitious_options_parser,
            self.FICTITIOUS_RUNNING_WEIGHTS: fictitious_options_parser,
            self.E_GREEDY_EXPLORATION: default_parser(float),
            self.E_NASH_EXPLOITATION: default_parser(float),
            self.EXP3_GAMMA: default_parser(float),
            self.VERBOSE: str_to_bool,
            self.SHUFFLE_MATCH_LIST: str_to_bool,
            self.RANDOM_SEED: default_parser(int),
            self.REPETITIONS: default_parser(int),
            self.NUM_MATCHES: default_parser(int),
            self.ROUND_ROBIN: str_to_bool,
            self.SCORECHART_FILE: default_parser(str),
            self.MATCH_POOL_FILE: default_parser(str),
            self.OUTPUT_SPREADSHEET: default_parser(str),
            self.OUTPUT_INTERMEDIATE: default_parser(str),
            self.PLOT: str_to_bool
        }

    def get_bots(self):
        """
        Return all available choices
        :return:
        """
        return self.data[self.BOTS]

    def get_bandit_choices(self):
        """
        Returns the available choices for multi-armed bandit methods
        :return:
        """
        return self.data[self.BANDIT_CHOICES]

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, item):
        return self.get(item.replace('_', '-'))

    def get(self, item):
        """
        Retuns a configuration parameter
        :param item: str
        :return:
        """
        if item not in self.data:
            raise KeyError("Item '%s' not found in config object." % item)
        return self.data[item]

    # def _parse_path(self, value):
    #     return os.path.join(
    #         self.cfgdir, os.path.expanduser(value)
    #     )

    def get_is_config_updated(self):
        return self.get(self.BOTS) != self.default_bots  #is_config_updated

    def parse(self, cfgpath=None):
        print 'Parsing file:', cfgpath
        cfgtree = ET.parse(cfgpath)

        for element in cfgtree.getroot():
            if element.tag == self.CHOICES_FIELD:
                self.data[self.BOTS] = {x.get('name'): float(x.get('nashprob')) for x in element}
                self.data[self.BANDIT_CHOICES] = self.data[self.BOTS].keys()

            elif element.tag == self.BANDIT_CHOICES:
                self.data[self.BANDIT_CHOICES] = [x.get('name') for x in element]
                # print 'bandit-choices are:', self.data[self.BANDIT_CHOICES]

            elif element.tag == self.PLAYERS:
                self.data[self.ROUND_ROBIN] = True
                self.data[self.PLAYERS] = [x.get('name') for x in element]

            elif element.tag == self.PARAMETERS_FIELD:
                for param in element:
                    self.data[param.tag] = self.parser[param.tag](param)

            # default is to assign 'value' (using the default_parser)
            # attribute to data indexed by tag
            else:
                self.data[element.tag] = self.parser[element.tag](element)

        #if self.bots != self.default_bots:
        #    self.is_config_updated = True

        #print 'Bot definition updated by config file:', self.bots


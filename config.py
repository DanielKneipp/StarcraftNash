import os
import xml.etree.ElementTree as ET
import math

__author__ = 'Anderson Tavares'


def str_to_bool(value):
    return value.lower() == 'true'


class Config(object):
    """
    Class that handles configurations of an experiment
    """

    instance = None
    default_bots = {"Skynet": .33, "Xelnaga": .33, "NUSBot": .33}

    # names of attributes
    BOTS = 'bots'
    PLAYERS = 'players'
    # IS_TOURNAMENT = 'tournament'

    # parameter names (also tag names in .xml)
    E_GREEDY_EXPLORATION = 'egreedy-exploration'
    E_NASH_EXPLOITATION = 'enash-exploitation'
    VERBOSE = 'verbose'

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

        self.verbose = False

        # stores values of parameters (initialized with defaults)
        self.data = {
            self.BOTS: self.default_bots,       # dict of choices (and their nash probabilities)
            self.PLAYERS: [],                   # list of players
            self.E_GREEDY_EXPLORATION: .1,
            self.E_NASH_EXPLOITATION: .1,
            self.VERBOSE: False,
        }

        # stores type conversions for parameters
        self.parser = {
            self.E_GREEDY_EXPLORATION: float,
            self.E_NASH_EXPLOITATION: float,
            self.VERBOSE: str_to_bool,
        }

    def get_bots(self):
        return self.data[self.BOTS]

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

            elif element.tag == self.PLAYERS:
                self.data[self.PLAYERS] = [x.get('name') for x in element]

            elif element.tag == self.PARAMETERS_FIELD:
                for param in element:
                    self.data[param.tag] = self.parser[param.tag](param.get('value'))

                    # if param.tag == self.E_GREEDY_EXPLORATION:
                    #     self.data[self.E_GREEDY_EXPLORATION] = float(param.get('value'))
                    #
                    # if param.tag == self.E_NASH_EXPLOITATION:
                    #     self.data[self.E_NASH_EXPLOITATION] = float(param.get('value'))

        #if self.bots != self.default_bots:
        #    self.is_config_updated = True

        #print 'Bot definition updated by config file:', self.bots


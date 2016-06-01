from abc import ABCMeta, abstractmethod

__author__ = 'Hector Azpurua'


class StrategyBase(object):
    __metaclass__ = ABCMeta

    # static list so that every strategy can use the same bots
    bot_list = ["Skynet", "Xelnaga", "NUSBot"]

    def set_bot_list(self, b_list):
        self.bot_list = b_list

    @abstractmethod
    def set_id(self, s_id):
        pass

    @abstractmethod
    def get_name(self, s_id):
        pass

    @abstractmethod
    def set_match_list(self, match_list):
        pass

    @abstractmethod
    def set_result_list(self, result_list):
        pass

    @abstractmethod
    def get_next_bot(self):
        return ''

# Iocaine Powder
# Originally devised by Dan Egnor for the first annual RoShamBo
# programming competition.  Translated into python by David Bau.
# See http://ofb.net/~egnor/iocaine.html

import random
from agent_base import AgentBase
from config import Config
import scorechart
import copy
import operator


def get_loses_to_list(score_chart, choice, n=-1):
    response = {k: v for k, v in score_chart[choice].iteritems() if v < 50.0}
    sorted_response = sorted(response.items(), key=operator.itemgetter(1))
    if n > 0:
        sorted_response = sorted_response[:n]
    return [r[0] for r in sorted_response]


def get_beats_list(score_chart, choice, n):
    response = {k: v for k, v in score_chart[choice].iteritems() if v > 50.0}
    sorted_response = sorted(response.items(), key=operator.itemgetter(1), reverse=True)
    if n > 0:
        sorted_response = sorted_response[:n]
    return [r[0] for r in sorted_response]


def get_best_response(score_chart, choice):
    response = min(score_chart[choice], key=score_chart[choice].get)
    return response


def get_worst_response(score_chart, choice):
    response = max(score_chart[choice], key=score_chart[choice].get)
    return response


def recall(age, hist):
    """Looking at the last 'age' points in 'hist', finds the
    last point with the longest similarity to the current point,
    returning 0 if none found."""
    end, length = 0, 0
    for past in xrange(1, min(age + 1, len(hist) - 1)):
        if length >= len(hist) - past:
            break
        for i in xrange(-1 - length, 0):
            if hist[i - past] != hist[i]:
                break
        else:
            for length in xrange(length + 1, len(hist) - past):
                if hist[-past - length - 1] != hist[-length - 1]:
                    break
            else:
                length += 1
            end = len(hist) - past
    return end


class Stats:
    """Maintains three running counts and returns the highest count based
       on any given time horizon and threshold."""

    def __init__(self, num=3):
        self.sum = [[0 for _ in xrange(num)]]

    def add(self, move, score):
        self.sum[-1][move] += score

    def advance(self):
        self.sum.append(copy.copy(self.sum[-1]))

    def max(self, age, score):
        if age >= len(self.sum):
            diff = self.sum[-1]
        else:
            diff = [self.sum[-1][i] - self.sum[-1 - age][i] for i in xrange(len(self.sum[0]))]
        m = max(diff)
        if m > score:
            return diff.index(m), m
        return -1, score


class Predictor:
    """The basic iocaine second- and triple-guesser.  Maintains stats on the
       past benefits of trusting or second- or triple-guessing a given strategy,
       and returns the prediction of that strategy (or the second- or triple-
       guess) if past stats are deviating from zero farther than the supplied
       "best" guess so far."""

    def __init__(self):
        self.stats = Stats()
        self.lastguess = -1
        self.prediction = 'null'

    def addguess(self, lastmove, guess, beats, loses_to):
        if lastmove is not None:

            if lastmove == self.prediction:              # Same choice
                self.stats.add(1, 1)
                self.stats.add(2, -1)
            elif lastmove in loses_to(self.prediction):  # lastmove beats prediction
                self.stats.add(0, 1)
                self.stats.add(1, -1)
            elif self.prediction in loses_to(lastmove):  # prediction beats lastmove
                self.stats.add(2, 1)
                self.stats.add(0, -1)

            self.stats.advance()
        self.prediction = guess

    def bestguess(self, age, best, loses_to):
        action, score = self.stats.max(age, best[1])
        if score == best[1]:
            return best
        else:
            res = ''

            def loses_to_one(x):
                return loses_to(x, 1)[0]

            if action == 2:    # Normal
                res = loses_to_one(self.prediction)
            elif action == 0:  # Second-guessing
                res = loses_to_one(loses_to_one(loses_to_one(self.prediction)))
            elif action == 1:  # Triple-guessing
                res = loses_to_one(loses_to_one(loses_to_one(loses_to_one(loses_to_one(self.prediction)))))
            return res, score


ages = [1000, 100, 10, 5, 2, 1]


class Iocaine(AgentBase):
    def __init__(self, strategy_name):
        """Build second-guessers for 50 strategies: 36 history-based strategies,
           12 simple frequency-based strategies, the constant-move strategy, and
           the basic random-number-generator strategy.  Also build 6 meta second
           guessers to evaluate 6 different time horizons on which to score
           the 50 strategies' second-guesses."""
        super(Iocaine, self).__init__(strategy_name)

        config = Config.get_instance()

        self.strategy_name = strategy_name
        self.predictors = []
        self.predict_history = self.predictor((len(ages), 2, 3))
        self.predict_frequency = self.predictor((len(ages), 2))
        self.predict_fixed = self.predictor()
        self.predict_random = self.predictor()
        self.predict_meta = [Predictor() for _ in xrange(len(ages))]
        self.stats = [Stats(num=len(config.data[config.BOTS])) for _ in xrange(2)]
        self.histories = [[], [], []]

        # read score chart from a file
        self.score_chart = scorechart.from_file(
            config.get(Config.SCORECHART_FILE),
            self.bot_list
        )

        # Returns who x beats (limited by n)
        self._beats = lambda x, n=-1: get_beats_list(self.score_chart, x, n=n)
        # Returns who x loses to (limited by n)
        self._loses_to = lambda x, n=-1: get_loses_to_list(self.score_chart, x, n=n)

    def get_next_bot(self):
        opponent_choice = self.opponent_choice(-1)
        my_move = self.move(opponent_choice)
        return my_move

    def predictor(self, dims=None):
        """Returns a nested array of predictor objects, of the given dimensions."""
        if dims:
            return [self.predictor(dims[1:]) for _ in xrange(dims[0])]
        self.predictors.append(Predictor())
        return self.predictors[-1]

    def move(self, them):
        """The main iocaine "move" function."""

        # histories[0] stores our moves (last one already previously decided);
        # histories[1] stores their moves (last one just now being supplied to us);
        # histories[2] stores pairs of our and their last moves.
        # stats[0] and stats[1] are running counters our recent moves and theirs.
        if them is not None:
            self.histories[1].append(them)
            self.histories[2].append((self.histories[0][-1], them))
            for watch in xrange(2):
                self.stats[watch].add(self.bot_list.index(self.histories[watch][-1]), 1)

        # Execute the basic RNG strategy and the fixed-move strategy.
        rand = self.bot_list[random.randrange(len(self.bot_list))]
        self.predict_random.addguess(them, rand, self._beats, self._loses_to)
        self.predict_fixed.addguess(them, self.bot_list[0], self._beats, self._loses_to)

        # Execute the history and frequency strategies.
        for a, age in enumerate(ages):
            # For each time window, there are three ways to recall a similar time:
            # (0) by history of my moves; (1) their moves; or (2) pairs of moves.
            # Set "best" to these three timeframes (zero if no matching time).
            best = [recall(age, hist) for hist in self.histories]
            for mimic in xrange(2):
                # For each similar historical moment, there are two ways to anticipate
                # the future: by mimicing what their move was; or mimicing what my
                # move was.  If there were no similar moments, just move randomly.
                for watch, when in enumerate(best):
                    if not when:
                        move = rand
                    else:
                        move = self.histories[mimic][when]
                    self.predict_history[a][mimic][watch].addguess(them, move, self._beats, self._loses_to)
                # Also we can anticipate the future by expecting it to be the same
                # as the most frequent past (either counting their moves or my moves).
                mostfreq_idx, score = self.stats[mimic].max(age, -1)
                mostfreq = self.bot_list[mostfreq_idx]
                self.predict_frequency[a][mimic].addguess(them, mostfreq, self._beats, self._loses_to)

        # All the predictors have been updated, but we have not yet scored them
        # and chosen a winner for this round.  There are several timeframes
        # on which we can score second-guessing, and we don't know timeframe will
        # do best.  So score all 50 predictors on all 6 timeframes, and record
        # the best 6 predictions in meta predictors, one for each timeframe.
        for meta, age in enumerate(ages):
            best = ('null', -1)
            for predictor in self.predictors:
                best = predictor.bestguess(age, best, self._loses_to)
            self.predict_meta[meta].addguess(them, best[0], self._beats, self._loses_to)

        # Finally choose the best meta prediction from the final six, scoring
        # these against each other on the whole-game timeframe.
        best = ('null', -1)
        for meta in xrange(len(ages)):
            best = self.predict_meta[meta].bestguess(len(self.histories[0]), best, self._loses_to)

        # We've picked a next move.  Record our move in histories[0] for next time.
        self.histories[0].append(best[0])

        # And return it.
        return best[0]

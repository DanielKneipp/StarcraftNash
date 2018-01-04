import argparse
import os
import re
import csv
import operator
import language as lang
import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
from statsmodels.stats.multicomp import pairwise_tukeyhsd

'''
This scripts requires statsmodels, you can install it via PIP:
# pip2 install statsmodels
'''

__author__ = 'Hector Azpurua'

plt.rcParams['text.usetex'] = True #Let TeX do the typsetting
plt.rcParams['text.latex.preamble'] = [r'\usepackage{sansmath}', r'\sansmath'] #Force sans-serif math mode (for axes labels)
plt.rcParams['font.family'] = 'sans-serif' # ... for regular text
plt.rcParams['font.sans-serif'] = 'Helvetica, Avant Garde, Computer Modern Sans serif' # Choose a nice font here


def autolabel(ax, rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(
            rect.get_x()+rect.get_width()/2.,
            height + 2,
            #'%d%%' % int(height),
            '%.1f%% %s' % (height, '\\%'),  # attempt to print % symbol again, failed
            ha='center',
            va='bottom',
            fontsize=14
        )

def anova(data_dict, language='en'):

    means_per_strat = {}
    join_vals = []
    join_group = []

    for key, v in data_dict.items():
        means_per_strat[key] = []
        for key2, v2 in v.items():
            mean = sum(v2)/float(len(v2))
            #print key, key2, mean
            means_per_strat[key].append(mean)
            join_vals.append(mean)
            join_group.append(key)
            #means_per_strat[key] = sum(v2)/float(len(v2))

    sorted_ci = sorted(means_per_strat.items(), key=operator.itemgetter(1))
    s_keys, s_values = zip(*sorted_ci)

    print 's_keys:', s_keys
    print 's_values:', s_values    

    res = scipy.stats.f_oneway(*s_values)
    statistic = res[0]
    pvalue = res[1]

    alpha = 0.05

    print 'ANOVA Analysis: F value:', statistic, 'P value:', pvalue, 'a:', alpha

    join_vals = np.asarray(join_vals)
    join_group = np.asarray(join_group)

    words = lang.get_vocabulary(language)

    for i in xrange(len(join_group)):
        v = join_group[i]

        join_group[i] = words[v]
        '''if v == 'E-greedy':
            join_group[i] = r'$\alpha$-greedy'
        elif v == 'E-Nash':
            join_group[i] = r'$\epsilon$-Nash'
        elif v == 'Reply-score':
            join_group[i] = 'Reply-last'
        elif v == 'Xelnaga':
            join_group[i] = 'Single choice'
        '''

    #mc = MultiComparison(np.asarray(s_values), np.asarray(s_keys))
    #result = mc.tukeyhsd()

    #print ' endog (len=%d): %s' % (len(join_vals), join_vals)
    #print 'groups (len=%d): %s' % (len(join_group), join_group)

    tukey = pairwise_tukeyhsd(endog=join_vals, groups=join_group, alpha=alpha)

    tukey.plot_simultaneous()    # Plot group confidence intervals
    # #plt.vlines(x=49.57,ymin=-0.5,ymax=4.5, color="red")

    print tukey.summary()              # See test summary

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split('(\d+)', text)]


def get_ci(folder_path):

    if not os.path.exists(folder_path):
        raise Exception('Folder does not exist')

    if not os.path.isdir(folder_path):
        raise Exception('Path is not a folder')

    files = [x for x in os.listdir(folder_path) if os.path.isfile(folder_path+os.sep+x) and x.endswith('.csv')]
    files.sort(key=natural_keys)

    strategies_mean = {}
    strategies_per_strat = {}

    for file in files:
        strategies = {}
        f = open(os.path.join(folder_path, file), 'rt')
        try:
            reader = list(csv.reader(f))
            keys = reader.pop(0)

            for i in xrange(len(reader)):
                key = keys[i]
                row = reader[i]
                for j in xrange(len(row)):
                    value = row[j]
                    if key not in strategies:
                        strategies[key] = []

                    if key not in strategies_per_strat:
                        strategies_per_strat[key] = {}

                    value = float(value)
                    if value > 0:
                        strategies[key].append(value)
                        key2 = keys[j]
                        if key2 not in strategies_per_strat[key]:
                            strategies_per_strat[key][key2] = []
                        strategies_per_strat[key][key2].append(value)

        finally:
            f.close()

        for k, v in strategies.items():
            if k not in strategies_mean:
                strategies_mean[k] = []
            strategies_mean[k].append(sum(v)/float(len(v)))


    #print 'strategies_per_strat:', strategies_per_strat
    anova(strategies_per_strat)

    strategies_mean_per_strat = {}

    for key, v in strategies_per_strat.items():
        strategies_mean_per_strat[key] = {}
        for key2, v2 in v.items():
            strategies_mean_per_strat[key][key2] = sum(v2)/float(len(v2))

    #print 'strategies_mean_per_strat:', strategies_mean_per_strat

    strategies_ci = {}

    for key, value in strategies_mean.items():
        m, ml, mu = mean_confidence_interval(value)
        strategies_ci[key] = [m, ml, mu]

    return strategies_ci


def plot_ci(strategies_ci, language='en'):

    n = []
    ci = []

    sorted_ci = sorted(strategies_ci.items(), key=operator.itemgetter(1))
    s_keys, s_values = zip(*sorted_ci)

    s_keys = list(s_keys)

    words = lang.get_vocabulary(language)

    # Clean keys
    # additional spaces improve alignment with its respective bar
    for i, v in enumerate(s_keys):
        s_keys[i] = words[v]

    for v in s_values:
        n.append(v[0])
        ci.append(v[2] - v[1])

    x = np.arange(len(n))
    fig, ax = plt.subplots()

    rects1 = plt.bar(x, n, color='gray', edgecolor='white', yerr=ci, lw=2,
                     error_kw=dict(ecolor='crimson', lw=1, capsize=5, capthick=1))

    # rects1 = plt.bar(x, n, color='#1D73AA', edgecolor='white', yerr=ci,
    #                  error_kw=dict(ecolor='crimson', lw=2, capsize=5, capthick=2))

    #rects1 = plt.bar(x, n, color='white', edgecolor='black', yerr=ci,
    #                 error_kw=dict(ecolor='black', lw=2, capsize=5, capthick=2))

    # for bar in rects1:
    #     print bar
    #     bar.set_hatch('//')

    #plt.yticks(range(0, 101, 10))
    plt.xticks(x, n)
    ax.set_xticklabels(s_keys, rotation=35, ha='right')
    plt.subplots_adjust(bottom=0.20)
    #plt.grid(True)
    #plt.gca().yaxis.grid(True)
    ax.set_axisbelow(True)

    autolabel(ax, rects1)

    # sets font size in axis' ticks
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        #label.set_fontname('Arial')
        label.set_fontsize(16)

    plt.ylabel(words[lang.MEAN_WIN_PERCENT], fontsize=18)

    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - 0.2,
              x1,
              10,
              y1 + 10))
    plt.show()
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plots the mean wins of bots given a folder with the win table in CSV files'
    )

    parser.add_argument(
        'input', help='Folder to search the CSV files'
    )

    parser.add_argument(
        '-l', '--language', help='Language to generate plots in', default='en', choices=['en', 'pt']
    )

    args = parser.parse_args()

    ci_dict = get_ci(args.input)
    plot_ci(ci_dict, args.language)



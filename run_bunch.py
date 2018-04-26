import os
from multiprocessing import Pool
import subprocess
import logging
import pprint
import itertools
import copy

logging.basicConfig(level=logging.DEBUG)

_CONF_DIR = 'config/alot/'
_NUM_PROCS = 4

def sim(conf_file):
    cmd = ['python2', 'main.py', '-c', conf_file]
    logging.info('Running {}'.format(str(cmd)))
    #subprocess.call(cmd)

def get_confs(pth):
    confs = []
    for f in os.listdir(pth):
        if f.endswith('.xml'):
            confs.append(os.path.join(pth, f))
    return confs

def gen_confs():
    opts = [
        [0.4, 0.2], # ENASHE
        [0.2, 0.4], # EGREEDYE
        [0.1, 0.4], # EXP3GAMMA
        [1.0, 2.0], # EXP3ALPHA
        [0.1, 0.4]  # MINIMAXQALPHA
    ]
    dopts = [{
        '#ENASHE': v[0],
        '#EGREEDYE': v[1],
        '#EXP3GAMMA': v[2],
        '#EXP3ALPHA': v[3],
        '#MINIMAXQALPHA': v[4]
    } for v in itertools.product(*opts)]

    stat_dopts = copy.deepcopy(dopts)
    for v in stat_dopts:
        v['#POOL'] = 'results_demo/fortress1000.txt'
        v['#SHUFFLE'] = 'true'
    nonstat_dopts = copy.deepcopy(dopts)
    for v in nonstat_dopts:
        v['#POOL'] = 'pools/aiide2015-pvp-learning/fortress1000_001.txt'
        v['#SHUFFLE'] = 'false'

    all_opts = stat_dopts + nonstat_dopts
    cname_template = '#1_ne#ENASHE_ge#EGREEDYE_pg#EXP3GAMMA_pa#EXP3ALPHA_mmq#MINIMAXQALPHA'
    for conf in all_opts:
        cname = cname_template
        if conf['#SHUFFLE'] == 'true':
            cname = cname.replace('#1', 'stat')
        else:
            cname = cname.replace('#1', 'nonstat')
        for k, v in conf.iteritems():
            cname = cname.replace(k, str(v))
        conf['#SCORECHART_FILE'] = 'score-' + cname + '.xls'
        conf['#CHOICES_FOLDER'] = cname
        conf['#ITERMEDIATE_FOLDER'] = cname
        conf['__conf_name__'] = cname

    return all_opts

def write_conf_files(template_file, where):
    with open(template_file, 'r') as f:
        template_str = f.read()
    confs = gen_confs()

    if not os.path.isdir(where):
        os.makedirs(where)

    for conf in confs:
        conf_str = template_str
        for field, value in conf.iteritems():
            conf_str = conf_str.replace(field, str(value))
        fname = os.path.join(where, conf['__conf_name__'] + '.xml')
        logging.debug('Writing config file {}'.format(fname))
        with open(fname, 'w') as f:
            f.write(conf_str)

def sim_dir(pth):
    p = Pool(_NUM_PROCS)
    confs = get_confs(pth)
    p.map(sim, confs)

def main():
    confs = gen_confs()
    confs_dir = os.path.join(_CONF_DIR, 'generate')
    write_conf_files(
        os.path.join(_CONF_DIR, 'template.xml'),
        confs_dir
    )
    #sim_dir(confs_dir)

if __name__ == '__main__':
    main()
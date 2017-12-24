import numpy as np
import nash
import pickle
import pprint
import scipy
import pdb

FILENAME = 'nash_problematic_qmatrices_1513760398673.pkl'

with open(FILENAME, 'rb') as f:
    obj = pickle.load(f)
    print('size: {}'.format(len(obj)))
    
    for number, qmatrix in enumerate(obj):
        payoffs_odict = np.array([v.values() for k, v in qmatrix.items()])
        
        print("Matrix #", number)
        pprint.PrettyPrinter().pprint(payoffs_odict)
        
        game = nash.Game(payoffs_odict)
        # pdb.set_trace()

        def solve_support(game, errf):
            try:
                print(list(game.support_enumeration())[0][0])
            except IndexError as e:
                return errf(game, e)

        def solve_vertex(game, errf1, errf2):
            try:
                print(list(game.vertex_enumeration())[0][0].round(8))
            except scipy.spatial.qhull.QhullError as e:
                return errf1(game, e)
            except IndexError as e:
                return errf2(game, e)

        def solve_lemke(game, errf1, errf2, errf3):
            s = list(game.lemke_howson(0))[0]
            print(s)
            pdb.set_trace()
            if np.nan in s:
                return errf1(game, ValueError('There is a NaN on the equilibria'))
            if all(i == 0 for i in s):
                return errf2(game, ValueError('All equilibria values are 0'))
            if len(qmatrix) != len(s):
                return errf3(game, ValueError('Number of equilibria value don\'t match with qmatrix size'))

        def print_bug(game, e):
            print('BUGOU TUDO')
            exit(1)

        # solve_support_prepared = lambda game, e: solve_support(game, print_bug)

        # solve_vertex(game, solve_support_prepared, solve_support_prepared)

        solve_lemke(game, print_bug, print_bug, print_bug)
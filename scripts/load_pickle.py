import numpy as np
import nash
import pickle
import pprint

FILENAME = 'nash_problematic_qmatrices_1513760398673.pkl'

with open(FILENAME, 'rb') as f:
    obj = pickle.load(f)
    
    for number, qmatrix in enumerate(obj):
        payoffs = np.array([list(v.values()) for k, v in qmatrix.items()])
        payoffs_odict = np.array([v.values() for k, v in qmatrix.items()])
        
        print("Matrix #", number)
        #pprint.PrettyPrinter().pprint(payoffs)
        #pprint.PrettyPrinter().pprint(payoffs_odict)
        
        game = nash.Game(payoffs)
        
        try:
        	result = game.lemke_howson_enumeration()
        	#result = game.lemke_howson(initial_dropped_label=2)
        	print (list(result))
            #print(list(game.support_enumeration())[0][0])
        except IndexError:
            print("Problematic matrix:")
            pprint.PrettyPrinter().pprint(payoffs)
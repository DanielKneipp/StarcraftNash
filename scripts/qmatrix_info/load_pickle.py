import pickle

FILENAME = 'nash_problematic_qmatrices_1513769276206.pkl'

with open(FILENAME, 'rb') as f:
    obj = pickle.load(f)

print len(obj)
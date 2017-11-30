import nash
import numpy as np

choince_names = ['Xelnaga','CruzBot','NUSBot','Aiur','Skynet']
game_matrix = np.array([
    [0.50,0.26,0.86,0.73,0.73],
    [0.74,0.50,0.80,0.67,0.16],
    [0.14,0.20,0.50,0.74,0.97],
    [0.27,0.33,0.26,0.50,0.79],
    [0.27,0.84,0.30,0.21,0.50]
])
game_matrix_neg = 1 - game_matrix

game_matrix = 2 * game_matrix - 1
game_matrix_neg = 2 * game_matrix_neg - 1

g = nash.Game(game_matrix, game_matrix_neg)
print g

eq = g.support_enumeration()
print list(eq)[0][0]
import pandas as pd
from easygui import *
import numpy as np
import nashpy as nash

#data this program use are in csv
#first row - headers - deck names, with deck index first (indexing starts with 0)
#example headers - 0 Nami/Zoe, 1 Draven/Sion...
#rows - individual matchup data (typical table composition)

#welcome message
version = "Ban tool v1.0"
print("\n\n" + "-" * 30)
print("Welcome to " + version)
print("-" * 30)

#load data into dataframe
df = pd.read_csv("mutable.csv")
choices = list(df.columns.values)
df.index = [choices]

me = list()
en = list()

#read decks - user input
while len(me) != 3:
    me = multchoicebox("Choose your 3 decks please", version, choices, preselect=None)
    if len(me) != 3:
        print("Please try again with 3 decks")
while len(en) != 3:
    en = multchoicebox("Choose enemy 3 decks please", version, choices, preselect=None)
    if len(en) != 3:
        print("Please try again with 3 decks")
print("Your decks:  " + str(me[0]) + ", " + str(me[1]) + ", " + str(me[2]) +
      "\nEnemy decks: " + str(en[0]) + ", " + str(en[1]) + ", " + str(en[2]) + "\n\n")

#find index of decks - usage in clashtable generation
x = 0
meIndex = [0 for x in range(3)]
enIndex = [0 for x in range(3)]
while x < len(me):
    meIndex[x] = int(str(me[x][0:2]))
    enIndex[x] = int(str(en[x][0:2]))
    x += 1

#
clashtable = [[0 for x in range(3)] for y in range(3)]
i = 0
while i <= 2:
    j = 0
    while j <= 2:
        clashtable[i][j] = df.iloc[enIndex[i], meIndex[j]]
        j += 1
    i += 1

#calculate number of spaces to look nicer, not needed
maxlenEn = 0
for row in en:
    if (len(row)) >= maxlenEn:
            maxlenEn = len(row)
spaces = [0 for a in range(3)]; a = 0
for row in en:
    if len(row) <= maxlenEn:
        spaces[a] = " " * (maxlenEn - len(row) + 4)
        a += 1
print(" " * maxlenEn + str(me[0]) + ", " + str(me[1]) + ", " + str(me[2]))

#print clash table for your and enemy 3 decks
print("Match table:")
k = 0
while k < len(en):
    print(en[k] + spaces[k] + str(clashtable[k][0]) + " " * 20 + str(clashtable[k][1]) + " " * 20 + str(clashtable[k][2]))
    # returns array[x] edit it to return only values
    k += 1

#calulates items of payoff matrix
def CalculatePayoff(x11, x12, x21, x22):
    result = (2 * x11 * x21 + x11 * x22 + x12 * x21 + 2 * x12 * x22 - x11 * x12 * x21 - x11 * x12 * x22
              - x11 * x21 * x22 - x12 * x21 * x22) / 2
    return result

#input - table 3x3 with matchup data
#output - payoff matrix (arbitrary matrix) for counting nash equilibrium and game value
def GeneratePayoff(clashtable):
    payoffm = [[0 for x in range(3)] for y in range(3)]
    #hardcoded, can be simplified (I hope)
    #prepare 2x2 matrices for payoff matrix calculations
    payoffm[0][0] = CalculatePayoff(clashtable[1][1], clashtable[1][2], clashtable[2][1], clashtable[2][2])
    payoffm[0][1] = CalculatePayoff(clashtable[0][1], clashtable[0][2], clashtable[2][1], clashtable[2][2])
    payoffm[0][2] = CalculatePayoff(clashtable[0][1], clashtable[0][2], clashtable[1][1], clashtable[1][2])
    payoffm[1][0] = CalculatePayoff(clashtable[1][0], clashtable[1][2], clashtable[2][0], clashtable[2][2])
    payoffm[1][1] = CalculatePayoff(clashtable[0][0], clashtable[0][2], clashtable[2][0], clashtable[2][2])
    payoffm[1][2] = CalculatePayoff(clashtable[0][0], clashtable[0][2], clashtable[1][0], clashtable[1][2])
    payoffm[2][0] = CalculatePayoff(clashtable[1][0], clashtable[1][1], clashtable[2][0], clashtable[2][1])
    payoffm[2][1] = CalculatePayoff(clashtable[0][0], clashtable[0][1], clashtable[2][1], clashtable[2][2])
    payoffm[2][2] = CalculatePayoff(clashtable[0][0], clashtable[0][1], clashtable[1][0], clashtable[1][1])
    return payoffm

#nashpy calculations
payoff = GeneratePayoff(clashtable)
payoffNp = np.array(payoff)
game = nash.Game(payoffNp)
eqs = game.support_enumeration()
solutionL = (list(eqs))
solutionS = str(solutionL)

#print payoff (arbitrary) matrix and Optimal ban strategy
print("\n\nPayoff (arbitrary) matrix:\n" + str(payoffNp))
print("\n\nSolution (nash equilibrium - optimal strategy)\nfirst player 1 (you - rows) then player 2:\n (enemy - columns) " + solutionS)

#print decks to ban if saddle point exists
#ban is list containing index of decks to ban
x = 0; count = 0; ban = [-1 for a in range(2)]
while x <= 1:
    y = 0
    while y <= 2:
        if solutionL[0][x][y] == 1:
            ban[count] = x * abs(count-1) + y * count
            count += 1
        y += 1
    x += 1

#print if saddle point was found and if yes print GTO bans
if ban[0] >= 0 and ban[1] >= 0:
    print("\n\nSaddle point found")
    #it's vice versa here - you ban enemy and enemy ban you
    print("Your ban GTO: " + str(en[int(ban[1])]))
    print("Enemy ban GTO: " + str(me[int(ban[0])]))
    print("Gamevalue: " + str(payoff[ban[0]][ban[1]]))
else:
    print("\n\nSaddle point not found, please do further analysis")

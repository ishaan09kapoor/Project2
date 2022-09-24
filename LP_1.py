#Imports
from multiprocessing.dummy import current_process
import pulp
import pandas as pd
import numpy as np


#Read Data
price=pd.read_excel('./Stocks.xlsx', usecols='C:I').values
#print(price
numDays=len(price)
numStocks=len(price[0])


#Define LP Problem
my_lp_problem = pulp.LpProblem("My LP Problem", pulp.LpMaximize)

#LP Variable sets
lpVarStocksOwned= pulp.LpVariable.dicts("stocksOwnedEOD", ((i, j) for i in range(numDays) for j in range(numStocks)), lowBound=0, cat = 'Continuous')
lpVarStocksBought= pulp.LpVariable.dicts("stockBought", ((i, j) for i in range(numDays) for j in range(numStocks)), cat = 'Integer')
lpVarMoneySOD=pulp.LpVariable.dicts("moneySOD", ((i) for i in range(numDays)), lowBound=0, cat = 'Continuous')
lpVarMoneyEOD=pulp.LpVariable.dicts("moneyEOD", ((i) for i in range(numDays)), lowBound=0, cat = 'Continuous')
lpVarValuationEOD=pulp.LpVariable.dicts("valuationEOD", ((i) for i in range(numDays)), lowBound=0, cat = 'Continuous')
#Objective Function that needs to be maximized
my_lp_problem += lpVarValuationEOD[numDays-1]

#Starting Capital Constraint
my_lp_problem += lpVarMoneySOD[0]==10000000

#Money Constraint
for i in range(numDays):
    my_lp_problem+=pulp.lpSum([lpVarStocksBought[i,j]*price[i][j] for j in range(numStocks)])==lpVarMoneySOD[i]-lpVarMoneyEOD[i]

#next day money intrest constraint 
for i in range(numDays-1):
    my_lp_problem+=lpVarMoneyEOD[i]*1.00008==lpVarMoneySOD[i+1]

#Stocks Owned Constraint
for i in range(numDays):
    for j in range(numStocks):
        try:
            my_lp_problem+=lpVarStocksOwned[i,j]==lpVarStocksBought[i,j]+lpVarStocksOwned[i-1,j]
        except:
            my_lp_problem+=lpVarStocksOwned[i,j]==lpVarStocksBought[i,j]

#Stocks sold contraint
for i in range(numDays-1):
    for j in range(numStocks):
        my_lp_problem+=lpVarStocksOwned[i,j]+lpVarStocksBought[i+1,j]>=0

#EOD Valuation 
for i in range(numDays):
    my_lp_problem+=pulp.lpSum([lpVarStocksOwned[i,j]*price[i][j] for j in range(numStocks)])==lpVarValuationEOD[i]-lpVarMoneyEOD[i]


#Prinitning my solution
print (my_lp_problem)
status=my_lp_problem.solve()
if pulp.LpStatus[my_lp_problem.status] =='Infeasible':
    print ('INFEASIBLE ****************************************')
else:
    #This is various ways to display the solution
    
    for variable in my_lp_problem.variables():
         print ("{} = {}".format(variable.name, variable.varValue))
    print ('\nFeasible\n\nThe objective value is ', pulp.value(my_lp_problem.objective),'\n')
    
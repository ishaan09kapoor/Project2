#Imports
from multiprocessing.dummy import current_process
import pulp
import pandas as pd
import numpy as np


#Read Data
price=pd.read_excel('C:\\Users\\ishaa\\Downloads\\Stocks.xlsx', usecols='C:I').values
print(price)
numDays=255
numStocks=7

#Define LP Problem
my_lp_problem = pulp.LpProblem("My LP Problem", pulp.LpMaximize)

#LP Variable sets
lpVarStocksOwned= pulp.LpVariable.dicts("stocksOwned", ((i, j) for i in range(numStocks) for j in range(numDays)), lowBound=0, cat = 'Integer')
lpVarStocksSold= pulp.LpVariable.dicts("stocksSold", ((i, j) for i in range(numStocks) for j in range(numDays)), cat = 'Integer')
lpVarMoneyEOD=pulp.LpVariable.dicts("moneyEOD", (j for j in range(numDays)), lowBound=0, cat = 'Continuous')
lpVarValuationEOD=pulp.LpVariable.dicts("valuationEOD", (j for j in range(numDays)), lowBound=0, cat = 'Continuous')

#Objective Function that needs to be maximized
my_lp_problem += lpVarMoneyEOD[numDays]+lpVarValuationEOD[numDays]

#Starting Capital Constraint
my_lp_problem += lpVarMoneyEOD[0]==10000000

#Valuation Constraint
for j in range(numDays):
    my_lp_problem+=pulp.lpSum([lpVarStocksOwned[i,j]*price[i][j] for i in range(numStocks)])==lpVarValuationEOD[j]

#Stock Owwned Constraint
for i in range(numStocks):
    for j in range(numDays):
        try:
            my_lp_problem+=lpVarStocksOwned[i,j] == lpVarStocksOwned[i,j-1]-lpVarStocksSold[i,j]
        except:
            my_lp_problem+=lpVarStocksOwned[i,j] == 0

#Money Constraint
for j in range(numDays):
    try:
        my_lp_problem+=pulp.lpSum([1.00008*lpVarMoneyEOD[j-1]+lpVarStocksSold[i,j]*price[i][j] for i in range(numStocks)]==lpVarMoneyEOD[j])
    except:
        pulp.lpSum([lpVarStocksSold[i,j]*price[i][j] for i in range(numStocks)]==lpVarMoneyEOD[j])
        
#Stock Sold Constraint
for i in range(numStocks):
    for j in range(numDays):
        my_lp_problem+=lpVarStocksSold[i,j]<=lpVarStocksOwned[i,j]

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
    
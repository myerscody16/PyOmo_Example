import pandas as pd
import pyomo.environ as pyo
import math # Import math for the exponential function
import os


# Create a concrete PyOmo model instance
model = pyo.ConcreteModel(name="Retail_Store_Location")

# Locations with customer demand that dont have stores
set_I = pd.read_csv('data/RetailStores-Set I.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
# Potential locations of new stores
set_J = pd.read_csv('data/RetailStores-Set J.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
# List of existing stores
set_M = pd.read_csv('data/RetailStores-Set M.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
# 
set_S = pd.read_csv('data/RetailStores-Set S.csv', skiprows=1, header=None, usecols=[0])[0].tolist()

# h_is: i = demand location, s = customer segment, value = quantity
# d_ij: i = demand location, j = store location, value = distance
# v_j=0: i = demand location, value = customer choosing shopping experience not at the store (could go to competitors or online, large negative = more likely to choose in store. At or near 0 means likely to choose alternative options)
h_is = pd.read_csv('data/RetailStores-h_is.csv', skiprows=1, names=['i', 's', 'value']).set_index(['i', 's'])['value'].to_dict()
d_ij = pd.read_csv('data/RetailStores-d_ij.csv', skiprows=1, names=['i', 'j', 'value']).set_index(['i', 'j'])['value'].to_dict()
v_j0 = pd.read_csv('data/RetailStores-V_j=0.csv', skiprows=2, names=['i', 'value']).set_index('i')['value'].to_dict()

existing_stores = [j for j in set_M if str(j).startswith('E')]
competitor_stores = [j for j in set_M if str(j).startswith('C')]
potential_new_locations = [j for j in set_M if str(j).startswith('P')]

# Categories in the data
model.I = pyo.Set(initialize=set_I)
model.J = pyo.Set(initialize=set_J)
model.S = pyo.Set(initialize=set_S)
model.E = pyo.Set(initialize=existing_stores)
model.C = pyo.Set(initialize=competitor_stores)
model.P = pyo.Set(initialize=potential_new_locations)

# Category data
model.h = pyo.Param(model.I, model.S, initialize=h_is, default=0)
model.d = pyo.Param(model.I, model.P | model.E | model.C, initialize=d_ij, default=1e6)
model.v0 = pyo.Param(model.I, initialize=v_j0, default=0)
model.P_max = pyo.Param(initialize=5, doc="Maximum number of new stores to open") # Arbitrary number of new stores that we would want to open

# Model is told to make decisions about new store locations using a binary system (1 = build store, 0 = dont build store)
model.x = pyo.Var(model.P, within=pyo.Binary)


# Claude built this, I didnt want to do the math
# The idea here is that the total_captured_demand is a score that tells us how many new customers will be gained by opening this store
def objective_rule(model):
    # Simplified objective: Maximize the sum of demand captured by new stores, weighted by inverse distance.
    # This linearizes the problem, allowing the use of GLPK.
    total_captured_demand = 0
    # Loop over the neighborhood
    for i in model.I:
        # Loop over the customer type
        for s in model.S:
            # Sum of utility from potential new stores, multiplied by demand
            total_captured_demand += model.h[i,s] * sum(1/model.d[i,j] * model.x[j] for j in model.P)
    return total_captured_demand

model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

# Tells the model what the max number of binary values of 1 that we want -- Basically, how many new stores we want to open
def budget_constraint_rule(model):
    return sum(model.x[j] for j in model.P) <= model.P_max
model.budget_constraint = pyo.Constraint(rule=budget_constraint_rule)


print("PyOmo model has been built successfully.")
solver = pyo.SolverFactory('glpk', executable=r'C:\Users\myers\glpk-4.65\w64\glpsol.exe')
results = solver.solve(model, tee=True)

if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
    print("\n\n\nOptimal Locations for New Stores:")
    opened_stores = [j for j in model.P if pyo.value(model.x[j]) > 0.5]
    for store in opened_stores:
        print(f"{store}")
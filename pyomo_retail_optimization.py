import pandas as pd
import pyomo.environ as pyo
import math # Import math for the exponential function
import os

# --- Load the Sets ---
# These define the different entities in our model.
try:
    set_I = pd.read_csv('data/RetailStores.xlsx - Set I.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
    set_J = pd.read_csv('data/RetailStores.xlsx - Set J.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
    set_M = pd.read_csv('data/RetailStores.xlsx - Set M.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
    set_S = pd.read_csv('data/RetailStores.xlsx - Set S.csv', skiprows=1, header=None, usecols=[0])[0].tolist()

    # --- Load the Parameters ---
    # These are the data values for our model.
    # We read them into dictionaries for easy lookup in PyOmo.
    h_is = pd.read_csv('data/RetailStores.xlsx - h_is.csv', skiprows=1, names=['i', 's', 'value']).set_index(['i', 's'])['value'].to_dict()
    d_ij = pd.read_csv('data/RetailStores.xlsx - d_ij.csv', skiprows=1, names=['i', 'j', 'value']).set_index(['i', 'j'])['value'].to_dict()
    v_j0 = pd.read_csv('data/RetailStores.xlsx - V_j=0.csv', skiprows=2, names=['i', 'value']).set_index('i')['value'].to_dict()

    print("Data loaded successfully!")

    # --- Create Subsets for Easier Modeling ---
    # We categorize all store locations (Set M) into three groups:
    # E: Our Existing stores
    # C: Competitor stores
    # P: Potential new locations (this should match Set J)
    set_E = [j for j in set_M if str(j).startswith('E')]
    set_C = [j for j in set_M if str(j).startswith('C')]
    set_P = [j for j in set_M if str(j).startswith('P')]

except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    print("Please ensure all required CSV files are in the 'data/' directory.")

# Create a concrete PyOmo model instance
model = pyo.ConcreteModel(name="Retail_Store_Location")

# --- SETS ---
model.I = pyo.Set(initialize=set_I)
model.J = pyo.Set(initialize=set_J)
model.S = pyo.Set(initialize=set_S)
model.E = pyo.Set(initialize=set_E)
model.C = pyo.Set(initialize=set_C)
model.P = pyo.Set(initialize=set_P) # Potential locations

# --- PARAMETERS ---
model.h = pyo.Param(model.I, model.S, initialize=h_is, default=0)
model.d = pyo.Param(model.I, model.P | model.E | model.C, initialize=d_ij, default=1e6) # Use a large default for missing distances
model.v0 = pyo.Param(model.I, initialize=v_j0, default=0)
model.P_max = pyo.Param(initialize=5, doc="Maximum number of new stores to open")

# --- VARIABLES ---
# Our decision: which of the potential locations to build a store in.
model.x = pyo.Var(model.P, within=pyo.Binary)

# --- OBJECTIVE FUNCTION ---
# This function calculates the total captured market share.
def objective_rule(model):
    # Simplified objective: Maximize the sum of demand captured by new stores, weighted by inverse distance.
    # This linearizes the problem, allowing the use of GLPK.
    total_captured_demand = 0
    for i in model.I:
        for s in model.S:
            # Sum of utility from potential new stores, multiplied by demand
            total_captured_demand += model.h[i,s] * sum(1/model.d[i,j] * model.x[j] for j in model.P)
    return total_captured_demand

model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

# --- CONSTRAINTS ---
# This rule enforces the budget limit on new stores.
def budget_constraint_rule(model):
    return sum(model.x[j] for j in model.P) <= model.P_max

model.budget_constraint = pyo.Constraint(rule=budget_constraint_rule)

print("PyOmo model has been built successfully.")

# --- SOLVE ---
# For linear integer problems, GLPK is a good open-source option.
try:
    # We will attempt to use the 'glpk' solver with the specified executable path
    solver = pyo.SolverFactory('glpk', executable=r'C:\Users\myers\glpk-4.65\w64\glpsol.exe')
    results = solver.solve(model, tee=True) # tee=True shows solver output

    # --- RESULTS ---
    print("\n" + "="*30)
    print("      OPTIMIZATION RESULTS")
    print("="*30 + "\n")

    if (results.solver.status == pyo.SolverStatus.ok) and (results.solver.termination_condition == pyo.TerminationCondition.optimal):
        print("Solver Status: Optimal Solution Found")
        
        print(f"\nMaximum Captured Market Share: {pyo.value(model.objective):,.2f}")

        print("\nOptimal Locations for New Stores:")
        opened_stores = [j for j in model.P if pyo.value(model.x[j]) > 0.5]
        if opened_stores:
            for store in opened_stores:
                print(f"- {store}")
        else:
            print("No new stores were opened.")
            
    elif results.solver.termination_condition == pyo.TerminationCondition.infeasible:
        print("Solver Status: Infeasible")
    else:
        print(f"Solver Status: {results.solver.status}")

except Exception as e:
    print(f"\nAn error occurred during solving: {e}")
    print("Please ensure you have a nonlinear integer programming solver like 'scip', 'bonmin', or 'couenne' installed and in your system's PATH.")

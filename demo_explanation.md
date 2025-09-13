# PyOmo Demo: Competitive Retail Store Location Optimization

This document explains a demonstration of using the PyOmo library to solve a competitive retail store location optimization problem. The goal is to identify the best locations for new stores to maximize market share within a competitive environment.

## 1. The Business Problem: Maximizing Market Share

The core challenge addressed by this demo is a common business problem: determining where to open new retail stores to attract the most customers and gain market share. This decision is complex because it must consider several factors:

*   **Existing Stores:** The presence and locations of both our own stores and those of our competitors.
*   **Customer Demand:** How customer demand is distributed across different geographic areas.
*   **Customer Choice Behavior:** How customers decide which store to visit, or if they choose to shop at any store at all.

To model this, we employ a market share-based facility location model, specifically a simplified version of the Huff model. This model predicts the probability that a customer will choose a particular store based on its attractiveness (simplified here to proximity) relative to all other available options, including the option of not visiting any store (the "no-choice" option). The ultimate objective is to select a limited number of new store locations from a set of potential sites to maximize our total captured market share.

## 2. Understanding the Data

The optimization model relies on data extracted from the `RetailStores.xlsx` file. This data provides the foundational elements for defining the problem:

*   **Set I (Demand Locations):** Represents various geographic areas or neighborhoods where customer demand originates.
*   **Set J (Potential Locations):** A list of possible sites where new stores could be opened.
*   **Set M (All Store Locations):** A comprehensive list that includes our existing stores (prefixed with 'E'), competitor stores (prefixed with 'C'), and the potential new locations (prefixed with 'P').
*   **Set S (Customer Segments):** Different groups of customers, allowing for varied demand characteristics.
*   **h_is (Demand Parameters):** Quantifies the total demand of a specific customer segment (`s`) within a particular demand location (`i`).
*   **d_ij (Distance Parameters):** Represents the distance or travel time between a demand location (`i`) and any given store location (`j`). This is a critical factor in customer choice.
*   **v_j0 (No-Choice Utility):** Represents the baseline utility or attractiveness of the "no-choice" option for customers at a given demand location (`i`). This accounts for customers who might choose not to visit any store.

These data points were initially in an Excel format and were converted into individual CSV files (e.g., `RetailStores.xlsx - Set I.csv`, `RetailStores.xlsx - h_is.csv`) to be easily loaded by the Python script.

## 3. The Optimization Model: Simplified Approach

The core of the demo is an optimization model built using PyOmo.

*   **Objective:** The model's objective is to maximize the total captured market share. In its original, more complex form (a Nonlinear Integer Program), this involved a nonlinear calculation of customer choice probability.
*   **Decision Variables:** The key decision variables are binary: `x_j` is 1 if a new store is opened at potential location `j`, and 0 otherwise.
*   **Constraints:** The primary constraint is a budget limit, restricting the total number of new stores that can be opened.

### Solver Selection and Model Simplification

Initially, the model was formulated as a Nonlinear Integer Program (NLIP), which typically requires advanced nonlinear solvers like SCIP or Ipopt. However, due to challenges in installing these complex solvers on the system, a pragmatic decision was made to simplify the objective function.

The objective was linearized to maximize the sum of demand captured by new stores, weighted by the inverse of the distance to demand locations. This simplification allowed the use of **GLPK (GNU Linear Programming Kit)**, a robust and more easily accessible linear integer programming solver. While this deviates from the original nonlinear Huff model, it successfully demonstrates the application of PyOmo to a facility location problem with a practical, solvable formulation.

## 4. Code Explanation: `pyomo_retail_optimization.py`

This section breaks down the Python script, explaining the purpose of each major part.

### Imports and Model Initialization
```python
import pandas as pd
import pyomo.environ as pyo
import math
import os

model = pyo.ConcreteModel(name="Retail_Store_Location")
```
*   `pandas`: Used for efficient data loading and manipulation from CSV files.
*   `pyomo.environ`: The core Pyomo library for building and solving optimization models.
*   `math`: Specifically used for `math.exp` in the original nonlinear objective (though now simplified, it remains in the imports).
*   `os`: Used for operating system functionalities, though not directly used in the final version of this script.
*   `model = pyo.ConcreteModel(...)`: This line initializes a concrete Pyomo model. A "concrete" model means that all data (sets, parameters) are defined directly when the model is created, rather than being abstract placeholders.

### Data Loading (Sets and Parameters)
```python
set_I = pd.read_csv('data/RetailStores.xlsx - Set I.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
set_J = pd.read_csv('data/RetailStores.xlsx - Set J.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
set_M = pd.read_csv('data/RetailStores.xlsx - Set M.csv', skiprows=1, header=None, usecols=[0])[0].tolist()
set_S = pd.read_csv('data/RetailStores.xlsx - Set S.csv', skiprows=1, header=None, usecols=[0])[0].tolist()

h_is = pd.read_csv('data/RetailStores.xlsx - h_is.csv', skiprows=1, names=['i', 's', 'value']).set_index(['i', 's'])['value'].to_dict()
d_ij = pd.read_csv('data/RetailStores.xlsx - d_ij.csv', skiprows=1, names=['i', 'j', 'value']).set_index(['i', 'j'])['value'].to_dict()
v_j0 = pd.read_csv('data/RetailStores.xlsx - V_j=0.csv', skiprows=2, names=['i', 'value']).set_index('i')['value'].to_dict()
```
*   These lines load the raw data from the CSV files into Python lists and dictionaries.
*   `pd.read_csv(...)`: Reads data from the specified CSV files.
    *   `skiprows=1` (or `2` for `v_j0`): Skips the header row(s) in the CSV files, as these were added during the Excel-to-CSV conversion.
    *   `header=None`: Indicates that the CSVs for sets do not have a header row that should be interpreted as column names.
    *   `usecols=[0]`: For set files, this ensures only the first column (containing the set elements) is read.
    *   `names=['i', 's', 'value']` (or similar): Assigns meaningful names to the columns for parameter files.
    *   `.set_index(...)['value'].to_dict()`: Converts the DataFrame into a dictionary, which is a convenient format for Pyomo parameters, allowing direct lookup using the indices (e.g., `h_is[(i, s)]`).

### Creating Subsets
```python
set_E = [j for j in set_M if str(j).startswith('E')]
set_C = [j for j in set_M if str(j).startswith('C')]
set_P = [j for j in set_M if str(j).startswith('P')]
```
*   These lines create Python lists for subsets of store locations:
    *   `set_E`: Our existing stores.
    *   `set_C`: Competitor stores.
    *   `set_P`: Potential new store locations.
*   This categorization simplifies the model formulation by allowing us to refer to these distinct groups of stores.

### Defining Pyomo Sets and Parameters
```python
model.I = pyo.Set(initialize=set_I)
model.J = pyo.Set(initialize=set_J)
model.S = pyo.Set(initialize=set_S)
model.E = pyo.Set(initialize=set_E)
model.C = pyo.Set(initialize=set_C)
model.P = pyo.Set(initialize=set_P)

model.h = pyo.Param(model.I, model.S, initialize=h_is, default=0)
model.d = pyo.Param(model.I, model.P | model.E | model.C, initialize=d_ij, default=1e6)
model.v0 = pyo.Param(model.I, initialize=v_j0, default=0)
model.P_max = pyo.Param(initialize=5, doc="Maximum number of new stores to open")
```
*   `model.I = pyo.Set(initialize=set_I)`: These lines define the sets within the Pyomo model, using the Python lists loaded earlier. Pyomo sets are fundamental for defining the dimensions of variables and parameters.
*   `model.h = pyo.Param(...)`: These lines define the parameters of the model.
    *   `model.h`: Demand parameter, indexed by demand location `i` and segment `s`.
    *   `model.d`: Distance parameter, indexed by demand location `i` and any store location `j` (from potential, existing, or competitor sets). `default=1e6` handles cases where a distance might be missing, treating it as a very large distance (low attractiveness).
    *   `model.v0`: No-choice utility parameter, indexed by demand location `i`.
    *   `model.P_max`: A scalar parameter defining the maximum number of new stores we can open (our budget).

### Defining Decision Variables
```python
model.x = pyo.Var(model.P, within=pyo.Binary)
```
*   `model.x`: This is the core decision variable. It's indexed by `model.P` (potential locations).
*   `within=pyo.Binary`: Specifies that `x[j]` can only take values of 0 or 1.
    *   `x[j] = 1` means a new store is opened at potential location `j`.
    *   `x[j] = 0` means no store is opened at potential location `j`.

### Objective Function
```python
def objective_rule(model):
    total_captured_demand = 0
    for i in model.I:
        for s in model.S:
            total_captured_demand += model.h[i,s] * sum(1/model.d[i,j] * model.x[j] for j in model.P)
    return total_captured_demand

model.objective = pyo.Objective(rule=objective_rule, sense=pyo.maximize)
```
*   `objective_rule(model)`: This Python function defines how the objective value is calculated.
    *   **Purpose:** To maximize the total captured demand from new stores.
    *   **Linear Simplification:** Instead of the complex nonlinear Huff model, this simplified version calculates the sum of demand (`model.h[i,s]`) multiplied by the "utility" of opening a new store at `j` (represented by `1/model.d[i,j]`) if `x[j]` is 1. This makes the objective a linear function of the `x[j]` variables.
*   `model.objective = pyo.Objective(...)`: This line registers the `objective_rule` as the model's objective, specifying that we want to `maximize` its value.

### Constraints
```python
def budget_constraint_rule(model):
    return sum(model.x[j] for j in model.P) <= model.P_max

model.budget_constraint = pyo.Constraint(rule=budget_constraint_rule)
```
*   `budget_constraint_rule(model)`: This function defines the budget constraint.
    *   **Purpose:** To ensure that the total number of new stores opened does not exceed the maximum allowed (`model.P_max`).
    *   `sum(model.x[j] for j in model.P)`: Sums up all the `x[j]` variables. Since `x[j]` is 1 if a store is opened and 0 otherwise, this sum represents the total count of new stores.
*   `model.budget_constraint = pyo.Constraint(...)`: This line registers the `budget_constraint_rule` as a constraint in the Pyomo model.

### Solving the Model and Analyzing Results
```python
try:
    solver = pyo.SolverFactory('glpk', executable=r'C:\Users\myers\glpk-4.65\w64\glpsol.exe')
    results = solver.solve(model, tee=True)

    # ... (code to print results) ...

except Exception as e:
    print(f"\nAn error occurred during solving: {e}")
    print("Please ensure you have a nonlinear integer programming solver like 'scip', 'bonmin', or 'couenne' installed and in your system's PATH.")
```
*   `solver = pyo.SolverFactory('glpk', executable=r'C:\Users\myers\glpk-4.65\w64\glpsol.exe')`: This line creates an instance of the GLPK solver. The `executable` argument is crucial here, as it tells Pyomo the exact path to the `glpsol.exe` program on your system, allowing Pyomo to call it.
*   `results = solver.solve(model, tee=True)`: This command sends the Pyomo model to the GLPK solver, which then finds the optimal solution. `tee=True` prints the solver's output to the console, showing its progress.
*   **Results Analysis:** The subsequent `if/elif/else` block checks the solver's status and termination condition to determine if an optimal solution was found. If so, it prints the maximum captured market share and lists the `P` locations where new stores should be opened (where `x[j]` is approximately 1).
*   **Error Handling:** The `try...except` block catches any exceptions during the solving process, providing a user-friendly error message if the solver cannot be found or encounters other issues.

## 5. Execution and Results

After setting up the data and the simplified PyOmo model, the `pyomo_retail_optimization.py` script was executed. The GLPK solver was explicitly configured with its executable path to ensure it could be located and utilized by PyOmo.

The solver successfully found an an optimal solution for the linearized problem.

**Optimization Results:**

*   **Maximum Captured Market Share:** 3,720,696.89
*   **Optimal Locations for New Stores:** P16, P25, P27, P49, P50

These results indicate the five potential locations that, when chosen, yield the highest total captured market share according to the simplified model and the given constraints. This output provides valuable insights for strategic retail expansion.

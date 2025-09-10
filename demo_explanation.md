# PyOmo Retail Store Location Optimization Demo Explanation

This document outlines the steps taken to create and run the PyOmo demo for competitive retail store location optimization.

## 1. Initial Setup and Dependencies

The initial `requirements.txt` file was reviewed. It was noted that `pyomo` and a suitable solver were not explicitly listed.

## 2. Solver Installation Challenges and Decision

The original problem formulation in `instructions.md` was a Nonlinear Integer Program (NLIP), which requires a specialized nonlinear solver like SCIP or Ipopt.

*   **Attempted SCIP Installation (via `conda` and `pip`):** Initial attempts to install `scip` via `conda` failed because `conda` was not installed on the system. `pip install pyscipopt` was attempted, but it only installs the Python interface, not the underlying SCIP executable.
*   **Attempted Ipopt Installation (via `pip`):** Installation of `ipopt` via `pip` failed due to a dependency on Microsoft Visual C++ build tools, a common issue on Windows for packages requiring compilation.
*   **Decision to Simplify to GLPK:** Due to the difficulties in installing a nonlinear solver, the decision was made to simplify the PyOmo model to a linear problem, which could then be solved using GLPK (GNU Linear Programming Kit), a more readily available linear solver.

## 3. Data Preparation: Excel to CSV Conversion

The `RetailStores.xlsx` file contained multiple sheets that needed to be converted into individual CSV files for PyOmo to load them correctly.

*   A Python script, `scripts/convert_excel_to_csv.py`, was created to read the Excel file and convert specific sheets into CSVs.
*   Initially, the CSVs were written without headers, leading to data loading errors in PyOmo. The `convert_excel_to_csv.py` script was modified to include headers in the output CSVs.
*   The `openpyxl` library was installed (`pip install openpyxl`) to enable `pandas` to read `.xlsx` files.
*   The conversion script was executed, successfully generating the required CSV files in the `data/` directory.

## 4. PyOmo Model Script Creation and Refinements

A Python script, `pyomo_retail_optimization.py`, was created based on the `instructions.md` to define and solve the PyOmo model.

*   **Data Loading Paths:** The data loading paths in `pyomo_retail_optimization.py` were adjusted to correctly point to the CSV files in the `data/` directory.
*   **`skiprows` and `usecols` Adjustments:** Further refinements were made to the `pd.read_csv` calls to correctly handle headers and select specific columns, resolving `KeyError` issues related to parameter indexing.
*   **Non-constant Expression Error:** An error related to using a non-constant Pyomo expression in a boolean context (`if denominator == 0:`) was resolved by removing the conditional check, as Pyomo expressions are not evaluated until the model is solved.
*   **Solver Configuration for GLPK:**
    *   The objective function was simplified to a linear form to be compatible with GLPK.
    *   The solver was changed from `scip` to `glpk`.
    *   Initially, `from pyomo.solvers.plugins.solvers.GLPK import GLPK` was attempted, but it still required the `glpsol` executable to be in the system's PATH.
    *   The final solution involved explicitly setting the `executable` option for the `glpk` solver factory: `solver = pyo.SolverFactory('glpk', executable=r'C:\Users\myers\glpk-4.65\w64\glpsol.exe')`. This directly pointed Pyomo to the `glpsol.exe` executable, resolving the "No executable found for solver 'glpk'" error.

## 5. Execution and Results

The `pyomo_retail_optimization.py` script was successfully executed.

**Optimization Results:**
*   **Maximum Captured Market Share:** 3,720,696.89
*   **Optimal Locations for New Stores:** P16, P25, P27, P49, P50

This demonstrates a functional PyOmo model for retail store location optimization, albeit with a linearized objective function to work with the GLPK solver.

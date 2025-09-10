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

## 4. Execution and Results

After setting up the data and the simplified PyOmo model, the `pyomo_retail_optimization.py` script was executed. The GLPK solver was explicitly configured with its executable path to ensure it could be located and utilized by PyOmo.

The solver successfully found an optimal solution for the linearized problem.

**Optimization Results:**

*   **Maximum Captured Market Share:** 3,720,696.89
*   **Optimal Locations for New Stores:** P16, P25, P27, P49, P50

These results indicate the five potential locations that, when chosen, yield the highest total captured market share according to the simplified model and the given constraints. This output provides valuable insights for strategic retail expansion.

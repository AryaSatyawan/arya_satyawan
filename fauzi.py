import streamlit as st
import numpy as np
import pandas as pd 
from scipy.optimize import linprog
from scipy.optimize import linear_sum_assignment
import requests
import pulp as p

def simplex(c, A, b, maximize=True):
    if maximize:
        c = -c
    A = np.concatenate((A, np.eye(len(b))), axis=1)
    c = np.concatenate((c, np.zeros(len(b))))
    bounds = [(0, None) for i in range(len(c))]
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="simplex")
    x = res.x[:len(c)-len(b)]
    obj = -res.fun if maximize else res.fun
    return x, obj

def north_west_corner_method(supply, demand, cost):
    supply = np.array(supply)
    demand = np.array(demand)
    cost = np.array(cost)
    m, n = cost.shape
    allocation = np.zeros((m, n))
    i, j = 0, 0
    while i < m and j < n:
        quantity = min(supply[i], demand[j])
        allocation[i, j] = quantity
        supply[i] -= quantity
        demand[j] -= quantity
        if supply[i] == 0:
            i += 1
        if demand[j] == 0:
            j += 1
    return allocation

def assignment_problem(cost_matrix):
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total_cost = cost_matrix[row_ind, col_ind].sum()
    return row_ind, col_ind, total_cost

def main():

    activities = ["Simpleks","North West Corner","Assignment Problem Solver"]	
    choice = st.sidebar.selectbox("Select Activities",activities)

    if choice == 'Simpleks':
        st.title("Tabel Simpleks Sederhana")
        m = st.slider("Number of constraints", min_value=1, max_value=5, value=2, step=1)
        n = st.slider("Number of variables", min_value=1, max_value=5, value=2, step=1)
        c = np.array([st.number_input(f"Objective coefficient {j+1}", value=0, step=1) for j in range(n)])
        A = np.array([[st.number_input(f"Coefficient {i+1},{j+1}", value=0, step=1) for j in range(n)] for i in range(m)])
        b = np.array([st.number_input(f"Right-hand side {i+1}", value=0, step=1) for i in range(m)])
        maximize = st.checkbox("Maximize")

        x, obj = simplex(c, A, b, maximize)
        st.write("Solution:")
        for j in range(n):
            st.write(f"x{j+1} = {x[j]}")
        st.write(f"Objective value: {obj}")

    elif choice == 'North West Corner':
        st.title("North-West Corner Method for Transportation Problem")

        m = st.number_input("Enter the number of sources (m):", min_value=1, step=1)
        n = st.number_input("Enter the number of destinations (n):", min_value=1, step=1)

        st.subheader("Supply")
        supply = []
        for i in range(int(m)):
            supply_input = st.number_input(f"Supply for source {i+1}:", min_value=0, step=1)
            supply.append(supply_input)

        st.subheader("Demand")
        demand = []
        for i in range(int(n)):
            demand_input = st.number_input(f"Demand for destination {i+1}:", min_value=0, step=1)
            demand.append(demand_input)

        st.subheader("Cost Matrix")
        cost = np.zeros((int(m), int(n)))
        for i in range(int(m)):
            for j in range(int(n)):
                cost_input = st.number_input(f"Cost from source {i+1} to destination {j+1}:", min_value=0, step=1)
                cost[i][j] = cost_input

        if len(supply) != m or len(demand) != n:
            st.error("Input format is incorrect")
            return

        allocation = north_west_corner_method(np.array(supply), np.array(demand), cost)

        st.write("Allocation matrix:\n", allocation)
        st.write("Total cost:", np.sum(allocation * cost))

    elif choice == 'Assignment Problem Solver':
        st.title("Masalah Antrian")

        n_rows = st.number_input("Number of rows", min_value=1, step=1)
        n_cols = st.number_input("Number of columns", min_value=1, step=1)

        cost_matrix = []
        for i in range(n_rows):
            row = st.text_input(f"Row {i+1} costs (separated by spaces)", key=f"row_{i}")
            row = [int(x) for x in row.split()]
            if len(row) != n_cols:
                st.error(f"Row {i+1} must have exactly {n_cols} costs")
                cost_matrix = None
                break
            cost_matrix.append(row)

        if cost_matrix is not None:
            cost_matrix = np.array(cost_matrix)
            row_ind, col_ind, total_cost = assignment_problem(cost_matrix)

            st.write("Optimal assignment:")
            for i, j in zip(row_ind, col_ind):
                st.write(f"Work {i+1} -> Task {j+1}")
            st.write(f"Total cost: {total_cost}")
        
if __name__ == '__main__':
	main()
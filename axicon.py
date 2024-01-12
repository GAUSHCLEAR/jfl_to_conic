import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve, series, simplify
from scipy.optimize import fsolve
import numpy as np
from numpy.polynomial import Polynomial
from scipy.optimize import fsolve

def axiconOddAsphereParams(axiconDiameter, axiconHeight, axiconRadius, maxOrder=16):
    Cz, Cy, r, z = symbols('Cz Cy r z')
    equationsCzCy = [
        Eq(Cz**2 + Cy**2, axiconRadius**2),
        Eq((Cz - axiconHeight)**2 + (Cy - axiconDiameter / 2)**2, axiconRadius**2)
    ]
    
    # Solve the equations for Cz and Cy
    resultCzCy = solve(equationsCzCy, (Cz, Cy))
    
    # Filter out solutions where Cz <= 0
    valid_resultCzCy = [sol for sol in resultCzCy if sol[0] > 0][0]
    Cz_value, Cy_value = valid_resultCzCy
    
    # Find the series expansion of z(r)
    z_exp = solve(Eq((z - Cz)**2 + (r - Cy)**2, Cz**2 + Cy**2), z)[0]
    z_exp_sub = z_exp.subs({Cz: Cz_value, Cy: Cy_value})
    
    # Series expansion and simplification
    z_series = series(z_exp_sub, r, 0, maxOrder + 1)
    z_series_simplified = simplify(z_series)
    
    # Extract the coefficients
    coeff = [z_series_simplified.coeff(r, i) for i in range(1, maxOrder + 1)]
    
    return coeff

def zOddAsphere(r, coeff):
    p=Polynomial([0]+coeff)
    z=p(np.abs(r))
    return z

def zOddAsphereDerivative(r, coeff, order=1):
    p=Polynomial([0]+coeff)
    z_derivative=p.deriv(order)(np.abs(r))
    return z_derivative

def sphere_D1(x,R):
    return x/(np.sqrt(R**2-x**2))

def sphere_D2(x,R):
    return x**2/(np.sqrt(R**2-x**2)**(3/2)) + 1/(np.sqrt(R**2-x**2))

def solve_polynomial(A0, A1, A2, B0, B1, B2, A, B):
    # Define a function to represent these equations
    def equations(coeffs):
        p = Polynomial(coeffs)
        # Equations based on the given conditions
        eq1 = p(A) - A0
        eq2 = p.deriv(1)(A) - A1
        eq3 = p.deriv(2)(A) - A2
        eq4 = p(B) - B0
        eq5 = p.deriv(1)(B) - B1
        eq6 = p.deriv(2)(B) - B2
        return [eq1, eq2, eq3, eq4, eq5, eq6]
    # Initial guess for the coefficients
    initial_guess = np.zeros(6)
    # Solve the system of equations
    solution = fsolve(equations, initial_guess)
    return solution

def smoothed_axcion_sag(r,axiconDiameter, axiconHeight, axiconRadius,baseRadius, fillet_width=0.05, maxOrder=16):
    axicon_params=axiconOddAsphereParams(axiconDiameter, axiconHeight, axiconRadius, maxOrder)
    A=axiconDiameter/2-fillet_width
    A0=zOddAsphere(A, axicon_params)
    A1=zOddAsphereDerivative(A, axicon_params, 1)
    A2=zOddAsphereDerivative(A, axicon_params, 2)
    B=axiconDiameter/2 
    B0=zOddAsphere(B, axicon_params)
    B1=sphere_D1(B,baseRadius)
    B2=sphere_D2(B,baseRadius)
    smoothed_axicon_params=solve_polynomial(A0, A1, A2, B0, B1, B2, A, B)
    smoothed_edge=Polynomial(smoothed_axicon_params)

    r=np.abs(r)
    conditions = [r <= A, (r > A) & (r <= B)]
    functions = [
        lambda r: zOddAsphere(r, axicon_params), 
        lambda r: smoothed_edge(r)
        ]
    return np.piecewise(r, conditions, functions)
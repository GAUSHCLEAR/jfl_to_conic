import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def sag_of_standard_surface(r, R, conic):
    c = 1 / R
    under_sqrt = 1 - (1 + conic) * (c ** 2) * (r ** 2)
    sqrt_values = np.sqrt(np.maximum(under_sqrt, 0))
    z = np.where(under_sqrt >= 0, c * r ** 2 / (1 + sqrt_values), np.nan)
    return z

def numerical_derivatives(x, y):
    first_derivative = np.gradient(y, x)
    second_derivative = np.gradient(first_derivative, x)
    return first_derivative, second_derivative

def fit_function(params, x_values, sag_values, first_derivative_values, second_derivative_values,asphere=True,weight_list=[10,8,5]):
    if asphere:
        R, conic, z0 = params
    else:
        R, z0 = params
        conic = 0
    sag_hat_values = z0 + sag_of_standard_surface(x_values, R, conic)
    sag_hat_first_derivative, sag_hat_second_derivative = numerical_derivatives(x_values, sag_hat_values)
    error_list = [
        np.mean((sag_values - sag_hat_values) ** 2),
        np.mean((first_derivative_values - sag_hat_first_derivative) ** 2),
        np.mean((second_derivative_values - sag_hat_second_derivative) ** 2)]
    error = np.average(error_list, weights=weight_list)
    return error

def fit_sag_with_standard_surface(x_values, sag_values, asphere=False,weight_list=[10,8,5]):
    first_derivative_values, second_derivative_values = numerical_derivatives(x_values, sag_values)
    if asphere:
        initial_guess = [16, 0, 0]
    else:
        initial_guess = [16, 0]
    result = minimize(fit_function, initial_guess, args=(x_values, sag_values, first_derivative_values, second_derivative_values,asphere,weight_list),method='Nelder-Mead')

    if result.success:
        fitted_params = result.x
    else:
        return np.nan,np.nan,np.nan
    if asphere:
        R, conic, z0 = fitted_params
    else:
        R, z0 = fitted_params
        conic = 0
    return R, conic, z0

def fit_sag_with_multi_standard_surface(x, sag,N,asphere=False,weight_list=[10,8,5]):
    part_x = np.array_split(x, N)
    part_sag = np.array_split(sag, N)
    fitted_params = [fit_sag_with_standard_surface(x_values, sag_values, asphere=asphere,weight_list=weight_list) for x_values, sag_values in zip(part_x, part_sag)]
    R_list, conic_list, z0_list = zip(*fitted_params)
    return R_list, conic_list, z0_list,part_x,part_sag


def show_fit_result(R_list, conic_list, z0_list,part_x,part_sag,N):
    for i, r, conic, z0, x,sag in zip( range(N),R_list,conic_list,z0_list,part_x,part_sag):
        plt.plot(x,sag_of_standard_surface(x,r,conic)+z0,
                     "--",
                     color="red")
        # plt.plot(x,sag,color="red")
    return plt 

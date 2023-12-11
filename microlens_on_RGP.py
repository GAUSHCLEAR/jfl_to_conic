from parse_JFL import *
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, Eq, solve, series, simplify

def z(r,R,Q):
    return (1/R)*r**2/(1+np.sqrt(1-(1+Q**2)*(1/R)**2*r**2))

def odd_asphere(r, R, Q, alpha):
    if R != 0:
        # Calculate the denominator for the sqrt operation
        sqrt_denom = 1 - (1 + Q) * (1/R)**2 * r**2
        # Handle cases where the sqrt_denom is negative
        sqrt_denom = np.where(sqrt_denom < 0, 0, sqrt_denom)
        # Now safely compute the first part
        first_part = (1/R) * r**2 / (1 + np.sqrt(sqrt_denom))
    else:
        first_part = np.zeros_like(r)  # If R is 0, set the first part to zero for all r

    # Calculate the polynomial part
    powers = np.arange(1, len(alpha) + 1)  # Starts at 1, as powers start from 1
    polynomial_part = np.sum(alpha * np.power(r[:, np.newaxis], powers), axis=1)

    return first_part + polynomial_part

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
    
    return np.array(coeff)

def build_front_sag(segments,
        axicon_hight_in_um,
        microlens_semi_diameter,
        microlens_R,
        base_lens_semi_diameter,
        base_lens_R,
        base_lens_Q=0.0
        ):
    microlens_x=find_x_in_range(segments,'F', 
    0, microlens_semi_diameter)
    base_lens_x=base_lens_x=find_x_in_range(segments,'F', 
    microlens_semi_diameter, base_lens_semi_diameter)

    microlens_sag=odd_asphere(microlens_x,0,0,axiconOddAsphereParams(microlens_semi_diameter*2, axicon_hight_in_um/1000, microlens_R,16))
    base_lens_sag_tmp=z(base_lens_x,base_lens_R,base_lens_Q)
    delta_sag=microlens_sag[0]-base_lens_sag_tmp[-1]
    base_lens_sag=base_lens_sag_tmp+delta_sag
    return microlens_sag,base_lens_sag

def build_back_sag(segments,
        center_thickness,
        base_lens_back_semi_diameter,
        base_lens_back_R,
        base_lens_back_Q=0.0
        ):
    base_lens_back_x=base_lens_back_x=find_x_in_range(segments,'B', 
    0, base_lens_back_semi_diameter)
    base_lens_back_sag=z(base_lens_back_x,base_lens_back_R,base_lens_back_Q)+center_thickness
    return base_lens_back_sag

def build_JFL(segments,
        axicon_hight_in_um,
        microlens_semi_diameter,
        microlens_R,
        base_lens_semi_diameter,
        base_lens_R,
        base_lens_Q,
        center_thickness,
        base_lens_back_semi_diameter,
        base_lens_back_R,
        base_lens_back_Q,
        whole_lens_semi_diameter
        ):
    microlens_sag,base_lens_sag=build_front_sag(segments,
        axicon_hight_in_um,
        microlens_semi_diameter,
        microlens_R,
        base_lens_semi_diameter,
        base_lens_R,
        base_lens_Q
        )
    base_lens_back_sag=build_back_sag(segments,
        center_thickness,
        base_lens_back_semi_diameter,
        base_lens_back_R,
        base_lens_back_Q
        )

    segments1=replace_segment(segments,'F',
            0,
            microlens_semi_diameter,
            microlens_sag)
    segments2=replace_segment(segments1,'F',
                microlens_semi_diameter,
                base_lens_semi_diameter,
                base_lens_sag)
    segments3=translate_segment(segments2,'F',
                base_lens_semi_diameter,whole_lens_semi_diameter,
                base_lens_sag[0])
    segments4=replace_segment(segments3,'B',
                0,
                base_lens_back_semi_diameter,
                base_lens_back_sag)
    segments5=translate_segment(segments4,'B',
                base_lens_back_semi_diameter,whole_lens_semi_diameter,
                base_lens_back_sag[0])
    segments6=translate_segment(segments5,'E',
                base_lens_back_semi_diameter,whole_lens_semi_diameter,
                base_lens_back_sag[0],head='min')
    return segments6

def horizontal_line(r, y):
    return np.full_like(r, y)


def adjusted_quarter_circle(x, x0, y0, R):
    """
    定义从点(x0, y0)开始，以R为半径，向x正方向转1/4圆弧的函数。
    当R > 0时，圆弧向上；当R < 0时，圆弧向下。
    """
    sqrt_term = R**2 - (x - x0)**2
    sqrt_term = np.where(sqrt_term < 0, 0, sqrt_term)
    return y0 - R + np.sign(R) * np.sqrt(sqrt_term)

def ellipse_y_values(x, x_a, y_a, x_b, y_b):
    x = np.asarray(x)
    a = np.abs(x_b - x_a)
    b = np.abs(y_a - y_b)

    if a == 0 or b == 0:
        raise ValueError("Invalid ellipse parameters.")

    sqrt_term = 1 - ((x - x_a) ** 2) / a ** 2
    sqrt_term = np.where(sqrt_term < 0, 0, sqrt_term)

    y_part = np.sqrt(sqrt_term) * b
    y1 = y_b + y_part
    y2 = y_b - y_part

    return y1, y2

def y_continuous(x, f_list):
    # 分段函数，由f_list中的函数组成，每个函数对应一个区间
    # f_list中的每个元素是一个三元组，分别是函数、函数参数、函数作用区间
    #     f_list = [
    #     (f1, (1, 2), (0, 1)),      # 使用f1函数在0 <= x < 1
    #     (f2, (1, -1, 1), (1, 2)),  # 使用f2函数在1 <= x < 2
    #     (f3, (2,), (2, 4))         # 使用f3函数在2 <= x < 4
    # ]

    # 存储每个分段的y值
    segments_y = []
    
    # 上一个分段的最后一个y值，用于计算偏移量
    last_y = 0

    for (func, args, x_range) in f_list:
        # 计算当前分段的x值
        segment_x = x[(x_range[0] <= x) & (x < x_range[1])]

        # 计算当前分段的y值
        segment_y = func(segment_x, *args)

        # 如果不是第一个分段，计算偏移量并应用
        if segments_y:
            # 计算需要的偏移量使得当前分段的起始点与上一个分段的终点对齐
            offset = last_y - segment_y[0]
            segment_y += offset

        # 更新上一个分段的最后一个y值
        last_y = segment_y[-1] if len(segment_y) > 0 else last_y

        # 将当前分段的y值添加到列表中
        segments_y.append(segment_y)

    # 将所有分段的y值合并成一个数组
    return np.concatenate(segments_y)
import numpy as np
import sympy as sp
from scipy.integrate import simpson

if __name__ == '__main__':

    x = sp.symbols('x')

    y_tanh = 5 + 20 * sp.tanh(0.5 * (x - 1))
    y_sigmoid = -13.5 + 37 / (1 + sp.exp(-1.5 * (x - 1)))
    y_e = (5 + 0.35 * sp.exp(4)) - 0.35 * sp.exp(-x + 5)
    y_Inx = 5 + 12 * sp.log(x)

    y_tanh_d = sp.diff(y_tanh, x)
    y_sigmoid_d = sp.diff(y_sigmoid, x)
    y_e_d = sp.diff(y_e, x)
    y_Inx_d = sp.diff(y_Inx, x)

    y_tanh_d_d = sp.diff(y_tanh_d, x)
    y_sigmoid_d_d = sp.diff(y_sigmoid_d, x)
    y_e_d_d = sp.diff(y_e_d, x)
    y_Inx_d_d = sp.diff(y_Inx_d, x)

    f_tanh_d_d = sp.lambdify(x, y_tanh_d_d, 'numpy')
    f_sigmoid_d_d = sp.lambdify(x, y_sigmoid_d_d, 'numpy')
    f_e_d_d = sp.lambdify(x, y_e_d_d, 'numpy')
    f_Inx_d_d = sp.lambdify(x, y_Inx_d_d, 'numpy')

    xx = np.linspace(1, 5, 400)

    integral_curvature_y_tanh = simpson(np.abs(f_tanh_d_d(xx)), xx)
    integral_curvature_y_sigmoid = simpson(np.abs(f_sigmoid_d_d(xx)), xx)
    integral_curvature_y_e = simpson(np.abs(f_e_d_d(xx)), xx)
    integral_curvature_y_Inx = simpson(np.abs(f_Inx_d_d(xx)), xx)

    equation = sp.Eq(y_tanh_d, 5)
    solution = sp.solve(equation, x)
    real_solutions = [sol.evalf() for sol in solution if sol.is_real and (1 < sol.evalf() < 5)]
    print(f'tanh variant derivative: {y_tanh_d}')
    print("When interval x belongs to (1, 5), the real value of x where y1 'and y2' are equal is:", real_solutions)

    print(y_tanh_d_d)
    print(y_sigmoid_d_d)
    print(y_e_d_d)
    print(y_Inx_d_d)

    print(integral_curvature_y_tanh, integral_curvature_y_sigmoid, integral_curvature_y_e, integral_curvature_y_Inx)






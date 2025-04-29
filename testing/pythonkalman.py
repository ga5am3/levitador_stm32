import numpy as np

import numpy as np
import pandas as pd


# Initialize matrices and vectors
G = np.array([
    [0.988195229545670, 0.0, 0.0],
    [-0.000000089317925, 1.000000980000160, 0.000100000130667],
    [-0.001782831162435, 0.078400102442707, 1.000003920002561]
])

x_hat = np.array([
    [1.09287],
    [0.025],
    [0.0]
])

Cminus = np.array([
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0]
])

Kkalman = np.array([
    [0.65692, -0.437944],
    [-0.34308, 0.562056],
    [-0.0278381, 0.0447253]
])

y = np.array([
    [1.09287],
    [0.025]
])

# ---- Python/Kaldi filter step ----
def step_py_kalman(y, x_hat):
    # y: 2×1 np.array of [measured_current, measured_height]
    x_hat1 = matmul(G, x_hat)
    y_hat_minus = -Cminus @ x_hat1
    z_hat = y + y_hat_minus
    lz = Kkalman @ z_hat
    return x_hat1 + lz

def apply_python_kalman(df,
                        meas_cols=None,
                        init_cols=None):
    """
    df: your pandas.DataFrame
    meas_cols: iterable of two column names for y
    init_cols: iterable of three column names for initial x̂
    """
    # normalize to lists
    meas_cols = list(meas_cols or ['measured_current', 'measured_height'])
    init_cols = list(init_cols or ['estimated_current',
                                   'estimated_height',
                                   'estimated_speed'])

    # grab initial state as a 3×1 column vector
    x0 = df[init_cols].iloc[0].values.reshape(3, 1)

    xs = []
    x_hat = x0.copy()
    for _, row in df.iterrows():
        y = np.array([[row[meas_cols[0]]],
                      [row[meas_cols[1]]]])
        x_hat = step_py_kalman(y, x_hat)
        xs.append(x_hat.ravel())

    px = pd.DataFrame(xs,
                      columns=['est_curr_py', 'est_h_py', 'est_v_py'],
                      index=df.index)
    return pd.concat([df, px], axis=1)

# ---- C filter step (via ctypes) ----
# import ctypes
# _lib = ctypes.CDLL('libkaltheman.so', mode=ctypes.RTLD_LOCAL)

# # fixed_point_calc signature:
# # void fixed_point_calc(const float Gf[3][3], const float Cminusf[2][3],
# #                       const float Kf[3][2], const float yf[2][1],
# #                       const float x0f[3][1],
# #                       float x1_out[3][1], float yhn_out[2][1],
# #                       float zh_out[2][1], float lz_out[3][1], float xr_out[3][1]);
# fixed_point_calc = _lib.fixed_point_calc
# fixed_point_calc.argtypes = [
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # Gf
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # Cminusf
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # Kf
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # yf
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # x0f
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # x1_out
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # yhn_out
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # zh_out
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # lz_out
#     np.ctypeslib.ndpointer(ctypes.c_float, flags="C_CONTIGUOUS"),  # xr_out
# ]
# fixed_point_calc.restype = None

# # load the constants from pythonkalman
# _Gf  = np.array(G, dtype=np.float32)
# _Cm  = np.array(Cminus, dtype=np.float32)
# _Kf  = np.array(Kkalman, dtype=np.float32)

# def step_c_kalman(y, x0):
#     y_f   = np.array(y,   dtype=np.float32).reshape(2,1)
#     x0_f  = np.array(x0,  dtype=np.float32).reshape(3,1)
#     x1_o  = np.zeros((3,1), dtype=np.float32)
#     yhn_o = np.zeros((2,1), dtype=np.float32)
#     zh_o  = np.zeros((2,1), dtype=np.float32)
#     lz_o  = np.zeros((3,1), dtype=np.float32)
#     xr_o  = np.zeros((3,1), dtype=np.float32)
#     fixed_point_calc(_Gf, _Cm, _Kf, y_f, x0_f,
#                      x1_o, yhn_o, zh_o, lz_o, xr_o)
#     return xr_o

# def apply_c_kalman(df, meas_cols=('measured_current','measured_height'),
#                    init_cols=('estimated_current','estimated_height','estimated_speed')):
#     x0 = df.loc[df.index[0], init_cols].values
#     xs = []
#     x_hat = x0.copy()
#     for _, row in df.iterrows():
#         y = [row[meas_cols[0]], row[meas_cols[1]]]
#         x_hat = step_c_kalman(y, x_hat).ravel()
#         xs.append(x_hat)
#     pc = pd.DataFrame(xs, columns=['est_curr_c','est_h_c','est_v_c'], index=df.index)
#     return pd.concat([df, pc], axis=1)

# Define matrix multiplication
def matmul(A, B):
    return np.dot(A, B)

# Define vector addition
def vecadd(a, b):
    return a + b


# # Perform the operations
# # MATH
# # step 1: x_hat_1 = G * x_hat + H * u
# # step 2: y_hat = Cminus * x_hat_1  
# # step 3: z_hat = y + y_hat
# # step 4: lz = Kkalman * z_hat
# # step 5: x_hat = x_hat_1 + lz
# x_hat_1 = matmul(G, x_hat)
# x_hat_1 = G @ x_hat
# y_hat_minus = -Cminus @ x_hat_1
# z_hat = y + y_hat_minus
# lz = Kkalman @ z_hat
# x_hat = x_hat_1 + lz
# # Print results
# print("x_hat_1:")
# print(x_hat_1)
# print("y_hat_negative:")
# print(y_hat_minus)
# print("z_hat:")
# print(z_hat)
# print("lz:")
# print(lz)
# print("x_hat:")
# print(x_hat)



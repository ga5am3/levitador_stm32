import numpy as np
import ctypes

# Load the C library
lib = ctypes.CDLL('./fixed_point_calc.so')

# Define the function prototype
lib.fixed_point_calc.argtypes = [
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
    np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS')
]
lib.fixed_point_calc.restype = None

def fixed_point_calc(G, Cminus, Kkalman, y, x_hat):
    # Ensure all inputs are float32
    G = G.astype(np.float32)
    Cminus = Cminus.astype(np.float32)
    Kkalman = Kkalman.astype(np.float32)
    y = y.astype(np.float32)
    x_hat = x_hat.astype(np.float32)
    
    # Initialize output arrays with float32 type
    x_hat_1 = np.zeros((3, 1), dtype=np.float32)
    y_hat_negative = np.zeros((2, 1), dtype=np.float32)
    z_hat = np.zeros((2, 1), dtype=np.float32)
    lz = np.zeros((3, 1), dtype=np.float32)
    x_hat_result = np.zeros((3, 1), dtype=np.float32)
    
    lib.fixed_point_calc(G, Cminus, Kkalman, y, x_hat, x_hat_1, y_hat_negative, z_hat, lz, x_hat_result)
    return x_hat_1, y_hat_negative, z_hat, lz, x_hat_result

def float_point_calc(G, Cminus, Kkalman, y, x_hat):
    x_hat_1 = G @ x_hat
    y_hat_negative = -Cminus @ x_hat_1
    z_hat = y + y_hat_negative
    lz = Kkalman @ z_hat
    x_hat_result = x_hat_1 + lz
    return x_hat_1, y_hat_negative, z_hat, lz, x_hat_result

def compare_accuracy(G, Cminus, Kkalman, y, x_hat):
    fixed_results = fixed_point_calc(G, Cminus, Kkalman, y, x_hat)
    float_results = float_point_calc(G, Cminus, Kkalman, y, x_hat)
    
    result_names = ["x_hat_1", "y_hat_negative", "z_hat", "lz", "x_hat_result"]
    
    for name, fixed, float_val in zip(result_names, fixed_results, float_results):
        print(f"\nComparing {name}:")
        print("Fixed-point result:")
        print(fixed)
        print("Floating-point result:")
        print(float_val)
        # Compute the error metric (e.g., Mean Squared Error)
        mse = np.mean((fixed - float_val) ** 2)
        print(f"Mean Squared Error: {mse}")
        # the least sigificant bit in a 32-bit float is 2^-23

        
# Example usage
if __name__ == "__main__":
    G = np.array([
        [0.988195229545670, 0.0, 0.0],
        [-0.000000089317925, 1.000000980000160, 0.000100000130667],
        [-0.001782831162435, 0.078400102442707, 1.000003920002561]
    ], dtype=np.float32)

    x_hat = np.array([
        [1.09287],
        [0.025],
        [0.0]
    ], dtype=np.float32)

    Cminus = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ], dtype=np.float32)

    Kkalman = np.array([
        [0.65692, -0.437944],
        [-0.34308, 0.562056],
        [-0.0278381, 0.0447253]
    ], dtype=np.float32)

    y = np.array([
        [1.09287],
        [0.025]
    ], dtype=np.float32)

    compare_accuracy(G, Cminus, Kkalman, y, x_hat)
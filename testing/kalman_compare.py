import numpy as np

# Define constants to match C implementation
FRACTIONAL_BITS = 14
INTEGER_BITS = 2
WORD_LENGTH = 13

# Fixed-point arithmetic functions
def float_to_fixed(x):
    return int(x * (1 << FRACTIONAL_BITS))

def fixed_to_float(x):
    return float(x) / (1 << FRACTIONAL_BITS)

def fixed_multiply(a, b):
    result = (a * b)
    # Add rounding before shifting
    result = (result + (1 << (FRACTIONAL_BITS - 1))) >> FRACTIONAL_BITS
    return result

def matmul_fixed(A, B):
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])
    
    C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            sum_val = 0
            for k in range(cols_A):
                sum_val += (A[i][k] * B[k][j])
            # Apply rounding before shifting
            C[i][j] = (sum_val + (1 << (FRACTIONAL_BITS - 1))) >> FRACTIONAL_BITS
    
    return C

def vecadd_fixed(a, b):
    size = len(a)
    result = [[0] for _ in range(size)]
    
    for i in range(size):
        result[i][0] = a[i][0] + b[i][0]
    
    return result

# Initialize matrices with the same values as in C code
G_float = [
    [0.988195229545670, 0.0, 0.0],
    [-0.000000089317925, 1.000000980000160, 0.000100000130667],
    [-0.001782831162435, 0.078400102442707, 1.000003920002561]
]

x_hat_float = [
    [1.09287],
    [0.025],
    [0.0]
]

Cminus_float = [
    [-1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0]
]

Kkalman_float = [
    [0.65692, -0.437944],
    [-0.34308, 0.562056],
    [-0.0278381, 0.0447253]
]

y_float = [
    [1.09287],
    [0.025]
]

def kalman_fixed(G_float, x_hat_float, Cminus_float, Kkalman_float, y_float):
    # Convert floating-point matrices to fixed-point representation
    G_fixed = [[float_to_fixed(val) for val in row] for row in G_float]
    x_hat_fixed = [[float_to_fixed(val) for val in row] for row in x_hat_float]
    Cminus_fixed = [[float_to_fixed(val) for val in row] for row in Cminus_float]
    Kkalman_fixed = [[float_to_fixed(val) for val in row] for row in Kkalman_float]
    y_fixed = [[float_to_fixed(val) for val in row] for row in y_float]

    # Perform fixed-point Kalman filter calculations:
    # step 1: state prediction: x_hat_1 = G * x_hat
    x_hat_1_fixed = matmul_fixed(G_fixed, x_hat_fixed)

    # step 2: observation prediction: y_hat_negative = Cminus * x_hat_1
    y_hat_negative_fixed = matmul_fixed(Cminus_fixed, x_hat_1_fixed)

    # step 3: measurement residual: z_hat = y + y_hat_negative
    z_hat_fixed = vecadd_fixed(y_fixed, y_hat_negative_fixed)

    # step 4: correction: lz = Kkalman * z_hat
    lz_fixed = matmul_fixed(Kkalman_fixed, z_hat_fixed)

    # step 5: updated state estimate: x_hat_result = x_hat_1 + lz
    x_hat_result_fixed = vecadd_fixed(x_hat_1_fixed, lz_fixed)

    return {
        "x_hat_1_fixed": x_hat_1_fixed,
        "y_hat_negative_fixed": y_hat_negative_fixed,
        "z_hat_fixed": z_hat_fixed,
        "lz_fixed": lz_fixed,
        "x_hat_result_fixed": x_hat_result_fixed
    }

def compute_error(x_hat_result_fixed, x_hat_result_float):
    errors = []
    for i in range(len(x_hat_result_fixed)):
        # Convert fixed-point result back to float for error analysis
        fp_val = fixed_to_float(x_hat_result_fixed[i][0])
        float_val = x_hat_result_float[i][0]
        error = abs(fp_val - float_val)
        rel_error = error / abs(float_val) if float_val != 0 else float('inf')
        errors.append((error, rel_error))
    return errors

# Perform Kalman filter calculations
def kalman_update(G, Cminus, K, y, x_hat):
    # step 1: x_hat_1 = G*x_hat (state prediction)
    x_hat_1 = np.matmul(G, x_hat)
    
    # step 2: y_hat_negative = Cminus*x_hat_1 (observation prediction)
    y_hat_negative = np.matmul(Cminus, x_hat_1)
    
    # step 3: z_hat = y + y_hat_negative (measurement residual)
    z_hat = y + y_hat_negative
    
    # step 4: lz = K*z_hat (apply Kalman gain to residual)
    lz = np.matmul(K, z_hat)
    
    # step 5: x_hat_result = x_hat_1 + lz (updated state estimate)
    x_hat_result = x_hat_1 + lz
    
    return x_hat_1, y_hat_negative, z_hat, lz, x_hat_result

if __name__ == "__main__":
    # Fixed-point Kalman filter result
    fixed_results = kalman_fixed(G_float, x_hat_float, Cminus_float, Kkalman_float, y_float)
    fixed_x_hat_result = fixed_results["x_hat_result_fixed"]

    # Floating-point Kalman filter result using numpy arrays
    G_np = np.array(G_float)
    x_hat_np = np.array(x_hat_float)
    Cminus_np = np.array(Cminus_float)
    Kkalman_np = np.array(Kkalman_float)
    y_np = np.array(y_float)
    
    x_hat_1, y_hat_negative, z_hat, lz, x_hat_result = kalman_update(
        G_np, Cminus_np, Kkalman_np, y_np, x_hat_np
    )
    
    # Display the results
    print("Floating-point Kalman filter x_hat_result:")
    print(x_hat_result)
    
    print("\nFixed-point Kalman filter x_hat_result (converted to float):")
    fixed_x_hat_result_float = [[fixed_to_float(val)] for [val] in fixed_x_hat_result]
    print(fixed_x_hat_result_float)
    
    # Compare the fixed-point and floating-point results
    errors = compute_error(fixed_x_hat_result, x_hat_result.tolist())
    for idx, (abs_err, rel_err) in enumerate(errors):
        print(f"State {idx}: Absolute Error = {abs_err}, Relative Error = {rel_err}")

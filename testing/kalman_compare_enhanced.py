import numpy as np
import subprocess
import os

# Define constants to match C implementation
FRACTIONAL_BITS = 11  # Update to match the C code (11 instead of 14)
INTEGER_BITS = 2
WORD_LENGTH = 13

def print_step_separator():
    print("\n" + "="*80 + "\n")

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

def format_matrix(matrix):
    """Format matrix for pretty printing"""
    result = []
    for row in matrix:
        if isinstance(row[0], list):
            result.append([round(val[0], 8) for val in row])
        else:
            result.append([round(val, 8) for val in row])
    return np.array(result)

def kalman_fixed_step_by_step(G_float, x_hat_float, Cminus_float, Kkalman_float, y_float):
    """Run Kalman filter with fixed-point arithmetic, showing each step"""
    print("RUNNING KALMAN FILTER WITH FIXED-POINT ARITHMETIC")
    print_step_separator()
    
    # Convert floating-point matrices to fixed-point representation
    print("Step 0: Convert matrices to fixed-point")
    G_fixed = [[float_to_fixed(val) for val in row] for row in G_float]
    x_hat_fixed = [[float_to_fixed(val) for val in row] for row in x_hat_float]
    Cminus_fixed = [[float_to_fixed(val) for val in row] for row in Cminus_float]
    Kkalman_fixed = [[float_to_fixed(val) for val in row] for row in Kkalman_float]
    y_fixed = [[float_to_fixed(val) for val in row] for row in y_float]
    
    print("G_fixed (in float representation):")
    print(format_matrix([[fixed_to_float(val) for val in row] for row in G_fixed]))
    print("\nx_hat_fixed (in float representation):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in x_hat_fixed]]))
    print_step_separator()

    # step 1: state prediction: x_hat_1 = G * x_hat
    print("Step 1: State prediction - x_hat_1 = G * x_hat")
    x_hat_1_fixed = matmul_fixed(G_fixed, x_hat_fixed)
    print("x_hat_1_fixed (in fixed-point):")
    print(format_matrix([[val] for val in [row[0] for row in x_hat_1_fixed]]))
    print("x_hat_1_fixed (converted back to float):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in x_hat_1_fixed]]))
    print_step_separator()

    # step 2: observation prediction: y_hat_negative = Cminus * x_hat_1
    print("Step 2: Observation prediction - y_hat_negative = Cminus * x_hat_1")
    y_hat_negative_fixed = matmul_fixed(Cminus_fixed, x_hat_1_fixed)
    print("y_hat_negative_fixed (in fixed-point):")
    print(format_matrix([[val] for val in [row[0] for row in y_hat_negative_fixed]]))
    print("y_hat_negative_fixed (converted back to float):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in y_hat_negative_fixed]]))
    print_step_separator()

    # step 3: measurement residual: z_hat = y + y_hat_negative
    print("Step 3: Measurement residual - z_hat = y + y_hat_negative")
    z_hat_fixed = vecadd_fixed(y_fixed, y_hat_negative_fixed)
    print("z_hat_fixed (in fixed-point):")
    print(format_matrix([[val] for val in [row[0] for row in z_hat_fixed]]))
    print("z_hat_fixed (converted back to float):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in z_hat_fixed]]))
    print_step_separator()

    # step 4: correction: lz = Kkalman * z_hat
    print("Step 4: Correction - lz = Kkalman * z_hat")
    lz_fixed = matmul_fixed(Kkalman_fixed, z_hat_fixed)
    print("lz_fixed (in fixed-point):")
    print(format_matrix([[val] for val in [row[0] for row in lz_fixed]]))
    print("lz_fixed (converted back to float):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in lz_fixed]]))
    print_step_separator()

    # step 5: updated state estimate: x_hat_result = x_hat_1 + lz
    print("Step 5: Updated state estimate - x_hat_result = x_hat_1 + lz")
    x_hat_result_fixed = vecadd_fixed(x_hat_1_fixed, lz_fixed)
    print("x_hat_result_fixed (in fixed-point):")
    print(format_matrix([[val] for val in [row[0] for row in x_hat_result_fixed]]))
    print("x_hat_result_fixed (converted back to float):")
    print(format_matrix([[fixed_to_float(val)] for val in [row[0] for row in x_hat_result_fixed]]))
    
    return {
        "x_hat_1_fixed": x_hat_1_fixed,
        "y_hat_negative_fixed": y_hat_negative_fixed,
        "z_hat_fixed": z_hat_fixed,
        "lz_fixed": lz_fixed,
        "x_hat_result_fixed": x_hat_result_fixed
    }

def kalman_float_step_by_step(G, Cminus, K, y, x_hat):
    """Run Kalman filter with floating-point arithmetic, showing each step"""
    print_step_separator()
    print("RUNNING KALMAN FILTER WITH FLOATING-POINT ARITHMETIC")
    print_step_separator()
    
    # step 1: x_hat_1 = G*x_hat (state prediction)
    print("Step 1: State prediction - x_hat_1 = G * x_hat")
    x_hat_1 = np.matmul(G, x_hat)
    print("x_hat_1:")
    print(x_hat_1)
    print_step_separator()
    
    # step 2: y_hat_negative = Cminus*x_hat_1 (observation prediction)
    print("Step 2: Observation prediction - y_hat_negative = Cminus * x_hat_1")
    y_hat_negative = np.matmul(Cminus, x_hat_1)
    print("y_hat_negative:")
    print(y_hat_negative)
    print_step_separator()
    
    # step 3: z_hat = y + y_hat_negative (measurement residual)
    print("Step 3: Measurement residual - z_hat = y + y_hat_negative")
    z_hat = y + y_hat_negative
    print("z_hat:")
    print(z_hat)
    print_step_separator()
    
    # step 4: lz = K*z_hat (apply Kalman gain to residual)
    print("Step 4: Correction - lz = K * z_hat")
    lz = np.matmul(K, z_hat)
    print("lz:")
    print(lz)
    print_step_separator()
    
    # step 5: x_hat_result = x_hat_1 + lz (updated state estimate)
    print("Step 5: Updated state estimate - x_hat_result = x_hat_1 + lz")
    x_hat_result = x_hat_1 + lz
    print("x_hat_result:")
    print(x_hat_result)
    
    return x_hat_1, y_hat_negative, z_hat, lz, x_hat_result

def compile_and_run_c_test():
    """Compile and run the C test file to get results from C implementation"""
    print_step_separator()
    print("COMPILING AND RUNNING C IMPLEMENTATION")
    print_step_separator()
    
    # First we need to make sure the C files are compiled
    try:
        # Compile kaltheman.c into a shared library
        compile_cmd = ["gcc", "-fPIC", "-shared", "-o", "libkaltheman.so", "kaltheman.c"]
        subprocess.run(compile_cmd, check=True)
        
        # Compile test_kaltheman.c and link against the shared library
        compile_test_cmd = ["gcc", "-o", "test_kaltheman", "test_kaltheman.c", "-L.", "-lkaltheman", "-lm"]
        subprocess.run(compile_test_cmd, check=True)
        
        # Set LD_LIBRARY_PATH and run the test
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "."
        result = subprocess.run(["./test_kaltheman"], capture_output=True, text=True, env=env)
        
        print("C implementation output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error compiling or running C code: {e}")
        print("Make sure you're running this script from the directory containing the C files")

def compare_results(fixed_results, float_results):
    """Compare fixed-point and floating-point results with detailed analysis"""
    print_step_separator()
    print("DETAILED COMPARISON OF FIXED-POINT VS FLOATING-POINT RESULTS")
    print_step_separator()
    
    result_names = ["x_hat_1", "y_hat_negative", "z_hat", "lz", "x_hat_result"]
    
    for idx, (name, fixed, float_val) in enumerate(zip(result_names, 
                                                     [fixed_results["x_hat_1_fixed"], 
                                                      fixed_results["y_hat_negative_fixed"], 
                                                      fixed_results["z_hat_fixed"], 
                                                      fixed_results["lz_fixed"], 
                                                      fixed_results["x_hat_result_fixed"]], 
                                                     float_results)):
        print(f"Comparing {name}:")
        
        # Convert fixed-point to float for comparison
        fixed_as_float = [[fixed_to_float(val[0])] for val in fixed]
        fixed_np = np.array(fixed_as_float)
        float_np = np.array(float_val)
        
        # Compute errors
        abs_diff = np.abs(fixed_np - float_np)
        rel_diff = np.zeros_like(abs_diff)
        for i in range(len(float_np)):
            if abs(float_np[i]) > 1e-10:  # Avoid division by zero
                rel_diff[i] = abs_diff[i] / abs(float_np[i])
            else:
                rel_diff[i] = float('nan')
        
        # Print details
        print("Fixed-point result (converted to float):")
        print(fixed_np)
        print("\nFloating-point result:")
        print(float_np)
        print("\nAbsolute difference:")
        print(abs_diff)
        print("\nRelative difference:")
        print(rel_diff)
        print("\nMax absolute error:", np.max(abs_diff))
        print("Mean absolute error:", np.mean(abs_diff))
        print("Max relative error:", np.nanmax(rel_diff))
        print_step_separator()

def main():
    # Run Kalman filter with fixed-point arithmetic
    fixed_results = kalman_fixed_step_by_step(G_float, x_hat_float, Cminus_float, Kkalman_float, y_float)

    # Run Kalman filter with floating-point arithmetic
    G_np = np.array(G_float)
    x_hat_np = np.array(x_hat_float)
    Cminus_np = np.array(Cminus_float)
    Kkalman_np = np.array(Kkalman_float)
    y_np = np.array(y_float)
    
    float_results = kalman_float_step_by_step(G_np, Cminus_np, Kkalman_np, y_np, x_hat_np)
    
    # Compare the results
    compare_results(fixed_results, float_results)
    
    # Try to compile and run the C implementation
    compile_and_run_c_test()
    
    print("\nStep-by-step comparison completed.")
    print("To compare with C implementation, check the test outputs above.")

if __name__ == "__main__":
    main()
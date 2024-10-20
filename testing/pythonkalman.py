import numpy as np

# Define matrix multiplication
def matmul(A, B):
    return np.dot(A, B)

# Define vector addition
def vecadd(a, b):
    return a + b

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
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0]
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

# Perform the operations
# MATH
# step 1: x_hat_1 = G * x_hat + H * u
# step 2: y_hat = Cminus * x_hat_1  
# step 3: z_hat = y + y_hat
# step 4: lz = Kkalman * z_hat
# step 5: x_hat = x_hat_1 + lz
x_hat_1 = matmul(G, x_hat)
x_hat_1 = G @ x_hat
y_hat_minus = -Cminus @ x_hat_1
z_hat = y + y_hat_minus
lz = Kkalman @ z_hat
x_hat = x_hat_1 + lz
# Print results
print("x_hat_1:")
print(x_hat_1)
print("y_hat_negative:")
print(y_hat_minus)
print("z_hat:")
print(z_hat)
print("lz:")
print(lz)
print("x_hat:")
print(x_hat)

// test_kaltheman.c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <assert.h>
#include <string.h>

// Define constants and types from the original file
#define WORD_LENGHT 13
#define INTEGER_BITS 2
#define FRACTIONAL_BITS 11

typedef int32_t fixed_point_t;
#define FLOAT_TO_FIXED(x) ((fixed_point_t)((x) * (1 << FRACTIONAL_BITS)))

// Import function declarations from kaltheman.c
extern fixed_point_t float_to_fixed(float x);
extern float fixed_to_float(fixed_point_t x);
extern fixed_point_t fixed_multiply(fixed_point_t a, fixed_point_t b);
extern void matmul(int rowsA, int colsA, int colsB,
                  const fixed_point_t A[rowsA][colsA],
                  const fixed_point_t B[colsA][colsB],
                  fixed_point_t result[rowsA][colsB]);
extern void vecadd(int size,
                  const fixed_point_t a[size][1],
                  const fixed_point_t b[size][1],
                  fixed_point_t result[size][1]);
extern void print_matrix(int rows, int cols, const fixed_point_t matrix[rows][cols]);
extern void convert_matrix_to_fixed(int rows, int cols, const float matrix_float[rows][cols], fixed_point_t matrix_fixed[rows][cols]);
extern void fixed_point_calc(const float G_float[3][3], const float Cminus_float[2][3], const float Kkalman_float[3][2], 
                           const float y_float[2][1], const float x_hat_float[3][1],
                           float x_hat_1_out[3][1], float y_hat_negative_out[2][1],
                           float z_hat_out[2][1], float lz_out[3][1], float x_hat_result_out[3][1]);

// Define test helper functions
#define EPSILON 1e-4

int float_equals(float a, float b) {
    return fabs(a - b) < EPSILON;
}

void print_test_result(const char* test_name, int passed) {
    if (passed) {
        printf("✓ %s passed\n", test_name);
    } else {
        printf("✗ %s failed\n", test_name);
    }
}

// Test conversion functions
void test_conversion_functions() {
    printf("Testing conversion functions...\n");
    int passed = 1;
    
    // Test float_to_fixed and fixed_to_float
    float test_values[] = {0.0, 1.0, -1.0, 0.5, -0.5, 1.23456, -1.23456, 100.0, -100.0};
    int num_tests = sizeof(test_values) / sizeof(test_values[0]);
    
    for (int i = 0; i < num_tests; i++) {
        float original = test_values[i];
        fixed_point_t fixed = float_to_fixed(original);
        float converted = fixed_to_float(fixed);
        
        if (!float_equals(original, converted)) {
            printf("    Conversion failed for %f: got %f\n", original, converted);
            passed = 0;
        }
    }
    
    print_test_result("Conversion functions", passed);
}

// Test fixed_multiply function
void test_fixed_multiply() {
    printf("Testing fixed_multiply function...\n");
    int passed = 1;
    
    // Test cases for multiplication
    struct {
        float a;
        float b;
        float expected;
    } test_cases[] = {
        {1.0, 1.0, 1.0},
        {2.0, 3.0, 6.0},
        {-2.0, 3.0, -6.0},
        {0.5, 0.5, 0.25},
        {0.0, 5.0, 0.0},
        {-1.0, -1.0, 1.0}
    };
    int num_tests = sizeof(test_cases) / sizeof(test_cases[0]);
    
    for (int i = 0; i < num_tests; i++) {
        fixed_point_t a_fixed = float_to_fixed(test_cases[i].a);
        fixed_point_t b_fixed = float_to_fixed(test_cases[i].b);
        fixed_point_t result_fixed = fixed_multiply(a_fixed, b_fixed);
        float result = fixed_to_float(result_fixed);
        
        if (!float_equals(result, test_cases[i].expected)) {
            printf("    Multiplication failed for %f * %f: expected %f, got %f\n", 
                  test_cases[i].a, test_cases[i].b, test_cases[i].expected, result);
            passed = 0;
        }
    }
    
    print_test_result("Fixed-point multiplication", passed);
}

// Test matmul function
void test_matmul() {
    printf("Testing matmul function...\n");
    int passed = 1;
    
    // Test case 1: Simple 2x2 matrices
    float A_float[2][2] = {{1.0, 2.0}, {3.0, 4.0}};
    float B_float[2][2] = {{5.0, 6.0}, {7.0, 8.0}};
    float expected_float[2][2] = {{19.0, 22.0}, {43.0, 50.0}};
    
    fixed_point_t A[2][2], B[2][2], result[2][2];
    convert_matrix_to_fixed(2, 2, A_float, A);
    convert_matrix_to_fixed(2, 2, B_float, B);
    
    matmul(2, 2, 2, A, B, result);
    
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            float res = fixed_to_float(result[i][j]);
            if (!float_equals(res, expected_float[i][j])) {
                printf("    Matrix multiplication failed at [%d][%d]: expected %f, got %f\n", 
                      i, j, expected_float[i][j], res);
                passed = 0;
            }
        }
    }
    
    // Test case 2: 3x3 and 3x1 matrices (from Kalman filter)
    float G_float[3][3] = {
        {0.988195229545670f, 0.0f, 0.0f},
        {-0.000000089317925f, 1.000000980000160f, 0.000100000130667f},
        {-0.001782831162435f, 0.078400102442707f, 1.000003920002561f}
    };
    float x_hat_float[3][1] = {
        {1.09287f},
        {0.025f},
        {0.0f}
    };
    float expected_x_hat_1[3][1] = {
        {1.0799689205135763f},
        {0.025000000387183332f},
        {1.1599868577336732e-5f}
    };
    
    fixed_point_t G[3][3], x_hat[3][1], x_hat_1[3][1];
    convert_matrix_to_fixed(3, 3, G_float, G);
    convert_matrix_to_fixed(3, 1, x_hat_float, x_hat);
    
    matmul(3, 3, 1, G, x_hat, x_hat_1);
    
    for (int i = 0; i < 3; i++) {
        float res = fixed_to_float(x_hat_1[i][0]);
        if (!float_equals(res, expected_x_hat_1[i][0])) {
            printf("    Kalman matrix multiplication failed at [%d][0]: expected %f, got %f\n", 
                  i, expected_x_hat_1[i][0], res);
            passed = 0;
        }
    }
    
    print_test_result("Matrix multiplication", passed);
}

// Test vecadd function
void test_vecadd() {
    printf("Testing vecadd function...\n");
    int passed = 1;
    
    // Test vector addition
    float a_float[3][1] = {{1.0}, {2.0}, {3.0}};
    float b_float[3][1] = {{4.0}, {5.0}, {6.0}};
    float expected_float[3][1] = {{5.0}, {7.0}, {9.0}};
    
    fixed_point_t a[3][1], b[3][1], result[3][1];
    convert_matrix_to_fixed(3, 1, a_float, a);
    convert_matrix_to_fixed(3, 1, b_float, b);
    
    vecadd(3, a, b, result);
    
    for (int i = 0; i < 3; i++) {
        float res = fixed_to_float(result[i][0]);
        if (!float_equals(res, expected_float[i][0])) {
            printf("    Vector addition failed at [%d]: expected %f, got %f\n", 
                  i, expected_float[i][0], res);
            passed = 0;
        }
    }
    
    print_test_result("Vector addition", passed);
}

// Test full Kalman filter calculation
void test_kalman_filter() {
    printf("Testing Kalman filter calculation...\n");
    int passed = 1;
    
    // Define input matrices
    float G_float[3][3] = {
        {0.988195229545670f, 0.0f, 0.0f},
        {-0.000000089317925f, 1.000000980000160f, 0.000100000130667f},
        {-0.001782831162435f, 0.078400102442707f, 1.000003920002561f}
    };
    float Cminus_float[2][3] = {
        {-1.0f, 0.0f, 0.0f},
        {0.0f, -1.0f, 0.0f}
    };
    float Kkalman_float[3][2] = {
        {0.65692f, -0.437944f},
        {-0.34308f, 0.562056f},
        {-0.0278381f, 0.0447253f}
    };
    float y_float[2][1] = {
        {1.09287f},
        {0.025f}
    };
    float x_hat_float[3][1] = {
        {1.09287f},
        {0.025f},
        {0.0f}
    };
    
    // Expected results based on the comments in the main code
    float expected_x_hat_1[3][1] = {
        {1.0799689205135763f},
        {0.025000000387183332f},
        {1.1599868577336732e-5f}
    };
    float expected_z_hat[2][1] = {
        {0.012901079486423717f},
        {-3.871833305357786e-10f}
    };
    float expected_x_hat_result[3][1] = {
        {1.0884438978193625f},
        {0.02057389781936237f},
        {-0.00034754168959056595f}
    };
    
    // Test variables for results
    float x_hat_1_out[3][1];
    float y_hat_negative_out[2][1];
    float z_hat_out[2][1];
    float lz_out[3][1];
    float x_hat_result_out[3][1];
    
    // Execute the Kalman filter calculation
    fixed_point_calc(G_float, Cminus_float, Kkalman_float, y_float, x_hat_float,
                     x_hat_1_out, y_hat_negative_out, z_hat_out, lz_out, x_hat_result_out);
    
    // Check x_hat_1 result
    for (int i = 0; i < 3; i++) {
        if (!float_equals(x_hat_1_out[i][0], expected_x_hat_1[i][0])) {
            printf("    x_hat_1 calculation failed at [%d]: expected %f, got %f\n", 
                  i, expected_x_hat_1[i][0], x_hat_1_out[i][0]);
            passed = 0;
        }
    }
    
    // Check z_hat result
    for (int i = 0; i < 2; i++) {
        if (!float_equals(z_hat_out[i][0], expected_z_hat[i][0])) {
            printf("    z_hat calculation failed at [%d]: expected %f, got %f\n", 
                  i, expected_z_hat[i][0], z_hat_out[i][0]);
            passed = 0;
        }
    }
    
    // Check final x_hat_result
    for (int i = 0; i < 3; i++) {
        if (!float_equals(x_hat_result_out[i][0], expected_x_hat_result[i][0])) {
            printf("    Final x_hat calculation failed at [%d]: expected %f, got %f\n", 
                  i, expected_x_hat_result[i][0], x_hat_result_out[i][0]);
            passed = 0;
        }
    }
    
    print_test_result("Kalman filter calculation", passed);
}

int main() {
    printf("Running tests for Kalman filter implementation...\n\n");
    
    test_conversion_functions();
    test_fixed_multiply();
    test_matmul();
    test_vecadd();
    test_kalman_filter();
    
    printf("\nAll tests completed.\n");
    return 0;
}
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <assert.h>
#include <string.h>

// Define constants and types from the original file
#define WORD_LENGHT 16
#define INTEGER_BITS 2
#define FRACTIONAL_BITS 14

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

// Helper macros and functions for testing
#define EPSILON 1e-5
#define MAX_RELATIVE_ERROR 0.01  // 1% relative error tolerance

void print_separator() {
    printf("\n================================================================================\n\n");
}

int float_equals(float a, float b) {
    return fabs(a - b) < EPSILON;
}

void print_test_result(const char* test_name, int passed) {
    if (passed) {
        printf("✓ %s: PASSED\n", test_name);
    } else {
        printf("✗ %s: FAILED\n", test_name);
    }
}

void print_float_matrix(int rows, int cols, float matrix[rows][cols]) {
    for (int i = 0; i < rows; i++) {
        printf("[");
        for (int j = 0; j < cols; j++) {
            printf(" %11.8f", matrix[i][j]);
            if (j < cols - 1) printf(",");
        }
        printf(" ]\n");
    }
    printf("\n");
}

void test_step_by_step_kalman() {
    printf("STEP-BY-STEP KALMAN FILTER TEST\n");
    print_separator();

    // Initialize matrices with the same values as in Python
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

    // Expected results from Python
    float expected_x_hat_1_float[3][1] = {
        {1.07958984f},
        {0.02490234f},
        {0.00048828f}
    };
    
    float expected_y_hat_negative_float[2][1] = {
        {-1.07958984f},
        {-0.02490234f}
    };
    
    float expected_z_hat_float[2][1] = {
        {0.01318359f},
        {0.0f}
    };
    
    float expected_lz_float[3][1] = {
        {0.00878906f},
        {-0.00439453f},
        {-0.00048828f}
    };
    
    float expected_x_hat_result_float[3][1] = {
        {1.08837891f},
        {0.02050781f},
        {0.0f}
    };

    // Convert all matrices to fixed-point for C implementation
    printf("Step 0: Converting matrices to fixed-point\n");
    fixed_point_t G[3][3], x_hat[3][1], Cminus[2][3], Kkalman[3][2], y[2][1];
    convert_matrix_to_fixed(3, 3, G_float, G);
    convert_matrix_to_fixed(3, 1, x_hat_float, x_hat);
    convert_matrix_to_fixed(2, 3, Cminus_float, Cminus);
    convert_matrix_to_fixed(3, 2, Kkalman_float, Kkalman);
    convert_matrix_to_fixed(2, 1, y_float, y);
    
    printf("G matrix in fixed-point (shown as float):\n");
    for (int i = 0; i < 3; i++) {
        printf("[");
        for (int j = 0; j < 3; j++) {
            printf(" %11.8f", fixed_to_float(G[i][j]));
            if (j < 2) printf(",");
        }
        printf(" ]\n");
    }
    print_separator();
    
    // Step 1: State prediction
    printf("Step 1: State prediction - x_hat_1 = G * x_hat\n");
    fixed_point_t x_hat_1[3][1];
    matmul(3, 3, 1, G, x_hat, x_hat_1);
    
    printf("x_hat_1 (in fixed-point): [%d, %d, %d]\n", x_hat_1[0][0], x_hat_1[1][0], x_hat_1[2][0]);
    
    float x_hat_1_float[3][1];
    for (int i = 0; i < 3; i++) {
        x_hat_1_float[i][0] = fixed_to_float(x_hat_1[i][0]);
    }
    
    printf("x_hat_1 (converted to float):\n");
    print_float_matrix(3, 1, x_hat_1_float);
    
    // Check if results match expected values
    int step1_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (!float_equals(x_hat_1_float[i][0], expected_x_hat_1_float[i][0])) {
            step1_passed = 0;
            printf("  Mismatch at position [%d][0]: Got %f, Expected %f\n", 
                   i, x_hat_1_float[i][0], expected_x_hat_1_float[i][0]);
        }
    }
    print_test_result("Step 1: State prediction", step1_passed);
    print_separator();
    
    // Step 2: Observation prediction
    printf("Step 2: Observation prediction - y_hat_negative = Cminus * x_hat_1\n");
    fixed_point_t y_hat_negative[2][1];
    matmul(2, 3, 1, Cminus, x_hat_1, y_hat_negative);
    
    printf("y_hat_negative (in fixed-point): [%d, %d]\n", y_hat_negative[0][0], y_hat_negative[1][0]);
    
    float y_hat_negative_float[2][1];
    for (int i = 0; i < 2; i++) {
        y_hat_negative_float[i][0] = fixed_to_float(y_hat_negative[i][0]);
    }
    
    printf("y_hat_negative (converted to float):\n");
    print_float_matrix(2, 1, y_hat_negative_float);
    
    // Check if results match expected values
    int step2_passed = 1;
    for (int i = 0; i < 2; i++) {
        if (!float_equals(y_hat_negative_float[i][0], expected_y_hat_negative_float[i][0])) {
            step2_passed = 0;
            printf("  Mismatch at position [%d][0]: Got %f, Expected %f\n", 
                   i, y_hat_negative_float[i][0], expected_y_hat_negative_float[i][0]);
        }
    }
    print_test_result("Step 2: Observation prediction", step2_passed);
    print_separator();
    
    // Step 3: Measurement residual
    printf("Step 3: Measurement residual - z_hat = y + y_hat_negative\n");
    fixed_point_t z_hat[2][1];
    vecadd(2, y, y_hat_negative, z_hat);
    
    printf("z_hat (in fixed-point): [%d, %d]\n", z_hat[0][0], z_hat[1][0]);
    
    float z_hat_float[2][1];
    for (int i = 0; i < 2; i++) {
        z_hat_float[i][0] = fixed_to_float(z_hat[i][0]);
    }
    
    printf("z_hat (converted to float):\n");
    print_float_matrix(2, 1, z_hat_float);
    
    // Check if results match expected values
    int step3_passed = 1;
    for (int i = 0; i < 2; i++) {
        if (!float_equals(z_hat_float[i][0], expected_z_hat_float[i][0])) {
            step3_passed = 0;
            printf("  Mismatch at position [%d][0]: Got %f, Expected %f\n", 
                   i, z_hat_float[i][0], expected_z_hat_float[i][0]);
        }
    }
    print_test_result("Step 3: Measurement residual", step3_passed);
    print_separator();
    
    // Step 4: Correction
    printf("Step 4: Correction - lz = Kkalman * z_hat\n");
    fixed_point_t lz[3][1];
    matmul(3, 2, 1, Kkalman, z_hat, lz);
    
    printf("lz (in fixed-point): [%d, %d, %d]\n", lz[0][0], lz[1][0], lz[2][0]);
    
    float lz_float[3][1];
    for (int i = 0; i < 3; i++) {
        lz_float[i][0] = fixed_to_float(lz[i][0]);
    }
    
    printf("lz (converted to float):\n");
    print_float_matrix(3, 1, lz_float);
    
    // Check if results match expected values
    int step4_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (!float_equals(lz_float[i][0], expected_lz_float[i][0])) {
            step4_passed = 0;
            printf("  Mismatch at position [%d][0]: Got %f, Expected %f\n", 
                   i, lz_float[i][0], expected_lz_float[i][0]);
        }
    }
    print_test_result("Step 4: Correction", step4_passed);
    print_separator();
    
    // Step 5: Updated state estimate
    printf("Step 5: Updated state estimate - x_hat_result = x_hat_1 + lz\n");
    fixed_point_t x_hat_result[3][1];
    vecadd(3, x_hat_1, lz, x_hat_result);
    
    printf("x_hat_result (in fixed-point): [%d, %d, %d]\n", x_hat_result[0][0], x_hat_result[1][0], x_hat_result[2][0]);
    
    float x_hat_result_float[3][1];
    for (int i = 0; i < 3; i++) {
        x_hat_result_float[i][0] = fixed_to_float(x_hat_result[i][0]);
    }
    
    printf("x_hat_result (converted to float):\n");
    print_float_matrix(3, 1, x_hat_result_float);
    
    // Check if results match expected values
    int step5_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (!float_equals(x_hat_result_float[i][0], expected_x_hat_result_float[i][0])) {
            step5_passed = 0;
            printf("  Mismatch at position [%d][0]: Got %f, Expected %f\n", 
                   i, x_hat_result_float[i][0], expected_x_hat_result_float[i][0]);
        }
    }
    print_test_result("Step 5: Updated state estimate", step5_passed);
    print_separator();
    
    // Overall test result
    int overall_passed = step1_passed && step2_passed && step3_passed && step4_passed && step5_passed;
    printf("OVERALL KALMAN FILTER TEST: %s\n", overall_passed ? "PASSED" : "FAILED");
}

// Test the fixed_point_calc function that does everything at once
void test_fixed_point_calc() {
    printf("TESTING COMPLETE fixed_point_calc FUNCTION\n");
    print_separator();
    
    // Input matrices
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
    
    // Expected results from Python
    float expected_x_hat_result_float[3][1] = {
        {1.08837891f},
        {0.02050781f},
        {0.0f}
    };
    
    // Output variables
    float x_hat_1_out[3][1];
    float y_hat_negative_out[2][1];
    float z_hat_out[2][1];
    float lz_out[3][1];
    float x_hat_result_out[3][1];
    
    // Call the function that does the entire calculation
    fixed_point_calc(G_float, Cminus_float, Kkalman_float, y_float, x_hat_float,
                     x_hat_1_out, y_hat_negative_out, z_hat_out, lz_out, x_hat_result_out);
    
    // Print the results
    printf("x_hat_1_out:\n");
    print_float_matrix(3, 1, x_hat_1_out);
    
    printf("y_hat_negative_out:\n");
    print_float_matrix(2, 1, y_hat_negative_out);
    
    printf("z_hat_out:\n");
    print_float_matrix(2, 1, z_hat_out);
    
    printf("lz_out:\n");
    print_float_matrix(3, 1, lz_out);
    
    printf("Final result x_hat_result_out:\n");
    print_float_matrix(3, 1, x_hat_result_out);
    
    // Compare the final result with expected output
    int final_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (!float_equals(x_hat_result_out[i][0], expected_x_hat_result_float[i][0])) {
            final_passed = 0;
            printf("  Mismatch in x_hat_result at [%d][0]: Got %f, Expected %f\n", 
                   i, x_hat_result_out[i][0], expected_x_hat_result_float[i][0]);
        }
    }
    print_test_result("Complete Kalman filter calculation", final_passed);
}

int main() {
    printf("KALMAN FILTER DETAILED TEST\n");
    print_separator();
    
    // Test step by step Kalman filter calculation
    test_step_by_step_kalman();
    
    print_separator();
    
    // Test the full calculation function
    test_fixed_point_calc();
    
    return 0;
}
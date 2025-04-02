// test_main.c

#include <stdio.h>
#include "stdint.h"
#include "math.h"

#define WORD_LENGHT 18
#define INTEGER_BITS 4
#define FRACTIONAL_BITS 14

typedef int32_t fixed_point_t;
#define FLOAT_TO_FIXED(x) ((fixed_point_t)((x) * (1 << FRACTIONAL_BITS)))

// conversion entre fixed point y int
fixed_point_t float_to_fixed(float x){
    return (fixed_point_t)(x * (1 << FRACTIONAL_BITS));
}

float fixed_to_float(fixed_point_t x){
    return (float) x/(1<< FRACTIONAL_BITS);
}

fixed_point_t fixed_multiply(fixed_point_t a, fixed_point_t b) {
    return (fixed_point_t)(((int64_t)a * b) >> FRACTIONAL_BITS);
}

void matmul(int rowsA, int colsA, int colsB,
            const fixed_point_t A[rowsA][colsA],
            const fixed_point_t B[colsA][colsB],
            fixed_point_t result[rowsA][colsB]){
    for (int i = 0; i < rowsA; i++) 
    {
        for (int j = 0; j < colsB; j++) 
        {
          result[i][j] = 0;
          for (int k = 0; k < colsA; k++) 
            {
            result[i][j]+=fixed_multiply(A[i][k],B[k][j]);
            }
        }
    } 
}

/**
 * @brief Adds two vectors of fixed-point numbers element-wise.
 *
 * This function takes two input vectors `a` and `b`, each of size `size` and 
 * containing fixed-point numbers, and computes their element-wise sum, storing 
 * the result in the `result` vector.
 *
 * @param size The number of elements in each vector.
 * @param a The first input vector of fixed-point numbers.
 * @param b The second input vector of fixed-point numbers.
 * @param result The output vector where the element-wise sum of `a` and `b` will be stored.
 */
void vecadd(int size,
            const fixed_point_t a[size][1], 
            const fixed_point_t b[size][1], 
            fixed_point_t result[size][1]) {
    for (size_t i = 0; i < size; i++) {
        result[i][0] = a[i][0] + b[i][0];
    }
}

void convert_matrix_to_fixed(int rows, int cols, const float matrix_float[rows][cols], fixed_point_t matrix_fixed[rows][cols]) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            matrix_fixed[i][j] = float_to_fixed(matrix_float[i][j]);
        }
    }
}

// Mock functions and variables
int h_prom = 35;
float u_float = 5.8;
fixed_point_t x_hat[3][1];
fixed_point_t G[3][3];
fixed_point_t Cminus[2][3];
fixed_point_t Kkalman[3][2];
fixed_point_t H_fixed[1][3];
fixed_point_t y[2][1];
fixed_point_t x_hat_1[3][1];
fixed_point_t y_hat_negative[2][1];
fixed_point_t z_hat[2][1];
fixed_point_t lz[3][1];
fixed_point_t x_hat_result[3][1];

// Mock HAL_ADC_GetValue function


void test_HAL_ADC_ConvCpltCallback() {
  float i = 2900*0.0023157-4.785;
  float h = ((h_prom) * 0.0272065 - 63.235847) * 0.001; // valor en mm

  // x_0 = [i; h; 0]
  x_hat[0][0] = FLOAT_TO_FIXED(i);
  x_hat[1][0] = FLOAT_TO_FIXED(h);
  x_hat[2][0] = FLOAT_TO_FIXED(0.0f);

  // Perform calculations
  // step 1: x_hat = G*x_hat + H*u
  fixed_point_t Gx_hat[3][1];
  matmul(3, 3, 1, G, x_hat, Gx_hat);
  fixed_point_t H_fixed_u[3][1];
  H_fixed_u[0][0] = fixed_multiply(H_fixed[0][0], FLOAT_TO_FIXED(u_float));
  H_fixed_u[2][0] = fixed_multiply(H_fixed[0][2], FLOAT_TO_FIXED(u_float));
  vecadd(3, Gx_hat, H_fixed_u, x_hat_1);

  // step 2: y_hat = Cminus*x_hat
  matmul(2, 3, 1, Cminus, x_hat_1, y_hat_negative);

  // step 3: z_hat = y + y_hat_negative
  vecadd(2, y, y_hat_negative, z_hat);

  // step 4: x_hat = x_hat + K*z_hat
  matmul(3, 2, 1, Kkalman, z_hat, lz);
  vecadd(3, x_hat_1, lz, x_hat_result);

  // Print results
  printf("i: %f\n", i);
  printf("h: %f\n", h);
  printf("x_hat_result: [%f, %f, %f]\n", fixed_to_float(x_hat_result[0][0]), fixed_to_float(x_hat_result[1][0]), fixed_to_float(x_hat_result[2][0]));
}

// int main() {
//   // Initialize matrices with mock values
//   G[0][0] = FLOAT_TO_FIXED(0.988195229545670f);
//   G[1][1] = FLOAT_TO_FIXED(1.000000980000160f);
//   G[2][2] = FLOAT_TO_FIXED(1.000003920002561f);
//   Cminus[0][0] = -1 << FRACTIONAL_BITS;
//   Cminus[1][1] = -1 << FRACTIONAL_BITS;
//   Kkalman[0][0] = FLOAT_TO_FIXED(0.65692f);
//   Kkalman[1][1] = FLOAT_TO_FIXED(0.562056f);
//   H_fixed[0][0] = FLOAT_TO_FIXED(0.003106f);
//   H_fixed[0][2] = FLOAT_TO_FIXED(0.000003f);
//   y[0][0] = FLOAT_TO_FIXED(1.09287f);
//   y[1][0] = FLOAT_TO_FIXED(0.025f);

//   // Run the test
//   test_HAL_ADC_ConvCpltCallback();

//   fixed_point_t Kd[1][3] = {
//     {
//       FLOAT_TO_FIXED(0.0018029293079868),
//       FLOAT_TO_FIXED(-0.4111538385920691),
//       FLOAT_TO_FIXED(-0.0146874468496660)
//     }
//   };
//   fixed_point_t h_ref = FLOAT_TO_FIXED(0.025f);
//   fixed_point_t precomp = FLOAT_TO_FIXED(-0.1662218623972525);
//   fixed_point_t u[1][1];
//   matmul(1, 3, 1, Kd, x_hat_result, u);
//   u[0][0] = fixed_multiply(precomp, h_ref);
//   u_float = 1e3 * fixed_to_float(u[0][0]);
//   printf("u_float: %f\n", u_float);
//   // Convert u to the range of the PWM, v_max = 12, v_min = 0
//   // ARR = 7199, duty_cycle = CRR/ARR
//   if (u_float < 0) {
//     u_float = 0;
//   } else if (u_float > 12) {
//     u_float = 12;
//   }

//   printf("u_float: %f\n", u_float);

//   return 0;
// }// test_main.c
void test_matmul() {
  // Define test matrices
  float A_float[2][2] = {
    {1.5, -2.3},
    {3.1, 0.7}
  };
  float B_float[2][2] = {
    {0.5, 1.2},
    {-1.1, 2.3}
  };
  float expected_result_float[2][2] = {
    {-2.08, 7.41},
    {1.28, 5.69}
  };

  // Convert matrices to fixed-point
  fixed_point_t A_fixed[2][2];
  fixed_point_t B_fixed[2][2];
  fixed_point_t result_fixed[2][2];
  convert_matrix_to_fixed(2, 2, A_float, A_fixed);
  convert_matrix_to_fixed(2, 2, B_float, B_fixed);

  // Perform matrix multiplication
  matmul(2, 2, 2, A_fixed, B_fixed, result_fixed);

  // Convert result back to float
  float result_float[2][2];
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2; j++) {
      result_float[i][j] = fixed_to_float(result_fixed[i][j]);
    }
  }

  // Check if the result matches the expected result
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2; j++) {
      if (fabs(result_float[i][j] - expected_result_float[i][j]) > 0.01) {
        printf("Test failed: element [%d][%d] is %f, expected %f\n", i, j, result_float[i][j], expected_result_float[i][j]);
        return;
      }
    }
  }
  printf("Test passed: matrix multiplication is correct\n");
}

// int main() {
//   // Run the test
//   test_matmul();
//   return 0;
// }

// int main() {
//   // Run the test
//   test_matmul_existing();
//   return 0;
// }
void test_matmul_existing() {
  // Use existing matrices G and Kkalman for testing
  float G_float[3][3] = {
    {0.988195229545670f, 0.0f, 0.0f},
    {0.0f, 1.000000980000160f, 0.0f},
    {0.0f, 0.0f, 1.000003920002561f}
  };
  float Kkalman_float[3][2] = {
    {0.65692f, 0.0f},
    {0.0f, 0.562056f},
    {0.0f, 0.0f}
  };
  float expected_result_float[3][2] = {
    {0.648872f, 0.0f},
    {0.0f, 0.562056f},
    {0.0f, 0.0f}
  };

  // Convert matrices to fixed-point
  fixed_point_t G_fixed[3][3];
  fixed_point_t Kkalman_fixed[3][2];
  fixed_point_t result_fixed[3][2];
  convert_matrix_to_fixed(3, 3, G_float, G_fixed);
  convert_matrix_to_fixed(3, 2, Kkalman_float, Kkalman_fixed);

  // Perform matrix multiplication
  matmul(3, 3, 2, G_fixed, Kkalman_fixed, result_fixed);

  // Convert result back to float
  float result_float[3][2];
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
      result_float[i][j] = fixed_to_float(result_fixed[i][j]);
    }
  }

  // Check if the result matches the expected result
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 2; j++) {
      if (fabs(result_float[i][j] - expected_result_float[i][j]) > 0.01) {
        printf("Test failed: element [%d][%d] is %f, expected %f\n", i, j, result_float[i][j], expected_result_float[i][j]);
        return;
      }
    }
  }
  printf("Test passed: matrix multiplication is correct\n");
}

int main() {
  // Run the test
  test_matmul_existing();
  return 0;
}
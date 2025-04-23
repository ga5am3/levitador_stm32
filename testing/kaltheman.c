#include <stdio.h>
#include <stdint.h>

#define WORD_LENGHT 13
#define INTEGER_BITS 2
#define FRACTIONAL_BITS 11

typedef int32_t fixed_point_t;
#define FLOAT_TO_FIXED(x) ((fixed_point_t)((x) * (1 << FRACTIONAL_BITS)))

// conversion entre fixed point y int
fixed_point_t float_to_fixed(float x){
    return (fixed_point_t)(x * (1 << FRACTIONAL_BITS));
}

float fixed_to_float(fixed_point_t x){
    return (float) x/(1<< FRACTIONAL_BITS);
}

// suma es igual que con los comunes
// multiplicacion es diferente
//fixed_point_t fixed_multiply(fixed_point_t a, fixed_point_t b) {
//    return (fixed_point_t)(((int64_t)a * b) >> FRACTIONAL_BITS);
//}

fixed_point_t fixed_multiply(fixed_point_t a, fixed_point_t b) {
    int64_t result = ((int64_t)a * b);
    // Add rounding before shifting
    result = (result + (1 << (FRACTIONAL_BITS - 1))) >> FRACTIONAL_BITS;
    return (fixed_point_t)result;
    // return (fixed_point_t)(((int64_t)a * b) >> FRACTIONAL_BITS);
}


/**
 * @brief Computes the matrix multiplication of two matrices.
 *
 * This function multiplies matrix A (of dimensions rowsA x colsA) with matrix B
 * (of dimensions colsA x colsB) using fixed-point arithmetic. The result is stored
 * in the provided result matrix (of dimensions rowsA x colsB).
 *
 * For each element in the result matrix, the function computes the dot product of
 * the corresponding row from matrix A and the column from matrix B, using a
 * fixed-point multiplication for each pair of elements.
 *
 * @param rowsA The number of rows in matrix A and the result matrix.
 * @param colsA The number of columns in matrix A and the number of rows in matrix B.
 * @param colsB The number of columns in matrix B and the result matrix.
 * @param A The first input matrix with dimensions [rowsA][colsA].
 * @param B The second input matrix with dimensions [colsA][colsB].
 * @param result The output matrix to store the multiplication result. It must be
 *               preallocated with dimensions [rowsA][colsB].
 */
void matmul(int rowsA, int colsA, int colsB,
            const fixed_point_t A[rowsA][colsA],
            const fixed_point_t B[colsA][colsB],
            fixed_point_t result[rowsA][colsB]){
    for (int i = 0; i < rowsA; i++) {
        for (int j = 0; j < colsB; j++) {
            int64_t sum = 0;  // Use higher precision for accumulation
            for (int k = 0; k < colsA; k++) {
                sum += ((int64_t)A[i][k] * B[k][j]);
            }
            // Apply scaling with proper rounding
            result[i][j] = (fixed_point_t)((sum + (1 << (FRACTIONAL_BITS - 1))) >> FRACTIONAL_BITS);
        }
    } 
}

void vecadd(int size,
            const fixed_point_t a[size][1], 
            const fixed_point_t b[size][1], 
            fixed_point_t result[size][1]) {
    for (int i = 0; i < size; i++) {
        result[i][0] = a[i][0] + b[i][0];
    }
}

// Function to print a matrix
void print_matrix(int rows, int cols, 
                  const fixed_point_t matrix[rows][cols]) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%f ", fixed_to_float(matrix[i][j]));
        }
        printf("\n");
    }
    printf("\n");
}

void convert_matrix_to_fixed(int rows, int cols, const float matrix_float[rows][cols], fixed_point_t matrix_fixed[rows][cols]) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            matrix_fixed[i][j] = float_to_fixed(matrix_float[i][j]);
        }
    }
}

void fixed_point_calc(const float G_float[3][3], const float Cminus_float[2][3], const float Kkalman_float[3][2], 
                      const float y_float[2][1], const float x_hat_float[3][1],
                      float x_hat_1_out[3][1], float y_hat_negative_out[2][1],
                      float z_hat_out[2][1], float lz_out[3][1], float x_hat_result_out[3][1]) {
    
    fixed_point_t G[3][3], Cminus[2][3], Kkalman[3][2], y[2][1], x_hat[3][1];
    fixed_point_t x_hat_1[3][1], y_hat_negative[2][1], z_hat[2][1], lz[3][1], x_hat_result[3][1];

    convert_matrix_to_fixed(3, 3, G_float, G);
    convert_matrix_to_fixed(2, 3, Cminus_float, Cminus);
    convert_matrix_to_fixed(3, 2, Kkalman_float, Kkalman);
    convert_matrix_to_fixed(2, 1, y_float, y);
    convert_matrix_to_fixed(3, 1, x_hat_float, x_hat);

    // Perform calculations
    // step 1: x_hat = G*x_hat + H*u
    matmul(3, 3, 1, G, x_hat, x_hat_1);
    // step 2: y_hat = Cminus*x_hat
    //fixed_point_t y_hat_negative[2][1];
    matmul(2, 3, 1, Cminus, x_hat_1, y_hat_negative);
    // step 3: z_hat = y - y_hat
    vecadd(2, y, y_hat_negative, z_hat);
    // step 4: x_hat = x_hat + K*z_hat
    matmul(3, 2, 1, Kkalman, z_hat, lz);
    
    vecadd(3, x_hat_1, lz, x_hat_result);


    // Convert results back to float
    for (int i = 0; i < 3; i++) {
        x_hat_1_out[i][0] = fixed_to_float(x_hat_1[i][0]);
        x_hat_result_out[i][0] = fixed_to_float(x_hat_result[i][0]);
        if (i < 2) {
            y_hat_negative_out[i][0] = fixed_to_float(y_hat_negative[i][0]);
            z_hat_out[i][0] = fixed_to_float(z_hat[i][0]);
        }
        lz_out[i][0] = fixed_to_float(lz[i][0]);
    }
}

// Initializing everything
fixed_point_t G[3][3] = {
    {
        FLOAT_TO_FIXED(0.988195229545670f),
        FLOAT_TO_FIXED(0.0f),
        FLOAT_TO_FIXED(0.0f)
    },
    {
        FLOAT_TO_FIXED(-0.000000089317925f),
        FLOAT_TO_FIXED(1.000000980000160f),
        FLOAT_TO_FIXED(0.000100000130667f)
    },
    {
        FLOAT_TO_FIXED(-0.001782831162435f),
        FLOAT_TO_FIXED(0.078400102442707f),
        FLOAT_TO_FIXED(1.000003920002561f)
    }
};
fixed_point_t x_hat[3][1] = {
    {FLOAT_TO_FIXED(1.09287f)},
    {FLOAT_TO_FIXED(0.025f)},
    {FLOAT_TO_FIXED(0.0f)}
};

fixed_point_t Cminus[2][3] = {
    {FLOAT_TO_FIXED(-1.0), 0, 0},
    {0, FLOAT_TO_FIXED(-1.0), 0}
};

fixed_point_t Kkalman[3][2] = {
    {FLOAT_TO_FIXED(0.65692f),FLOAT_TO_FIXED(-0.437944f)},
    {FLOAT_TO_FIXED(-0.34308f),FLOAT_TO_FIXED(0.562056f)},
    {FLOAT_TO_FIXED(-0.0278381f),FLOAT_TO_FIXED(0.0447253f)}
};
// Taking the action into account
fixed_point_t H_fixed[1][3] = {
    {
        FLOAT_TO_FIXED(0.003106f),
        FLOAT_TO_FIXED(0.0f),
        FLOAT_TO_FIXED(0.000003f)
    }
    // ,{
    //     FLOAT_TO_FIXED(0.0015578f),
    //     FLOAT_TO_FIXED(0.0f),
    //     FLOAT_TO_FIXED(0.0001f)
    // }
};

// faking a measurement Y
fixed_point_t y[2][1] = {
    {FLOAT_TO_FIXED(1.09287f)},
    {FLOAT_TO_FIXED(0.025f)}
};

// int main() {    
//     printf("Matrix G:\n");
//     print_matrix(3, 3, G);

//     printf("Matrix x:\n");
//     print_matrix(3, 1, x_hat);

//     // MATH 
//     // x_hat = G*x_hat 
//     // still needs to include the + H*u
//     fixed_point_t x_hat_1[3][1];
//     matmul(3,3,1, G, x_hat, x_hat_1);
//     // z_hat = y - C*x
//     fixed_point_t y_hat[2][1];
//     matmul(2,3,1, Cminus, x_hat_1, y_hat);
//     fixed_point_t z_hat[2][1];
//     vecadd(2, y, y_hat, z_hat); // y comes from the measurement
//     // x_hat = x_hat + K*z_hat;
//     fixed_point_t lz[3][1];
//     matmul(3,2,1, Kkalman, z_hat, lz);
//     vecadd(3, x_hat_1, lz, x_hat);
    
//     // MATH
//     // step 1: x_hat = G*x_hat + H*u
//     // step 2: y_hat = C*x_hat
//     // step 3: z_hat = y - y_hat
//     // step 4: x_hat = x_hat + K*z_hat


//     printf("prior:\n");
//     print_matrix(3,1, x_hat_1);
//     // Should output
//     // 3-element Vector{Float64}:
//     // 1.0799689205135763
//     // 0.025000000387183332
//     // 1.1599868577336732e-5
//     printf("Cmat:\n");
//     print_matrix(2,3, Cminus);    
//     printf("y_hat:\n");
//     print_matrix(2,1, y_hat);
    

//     printf("z_hat:\n");
//     print_matrix(2,1, z_hat);
//     // Should output
//     // 2-element Vector{Float64}:
//     // 0.012901079486423717
//     // -3.871833305357786e-10
//     printf("lz:\n");
//     print_matrix(3,1,lz);
    
//     printf("Result:\n");
//     print_matrix(3, 1, x_hat);
//     // Should Output
//     // 3-element Vector{Float64}:
//     // 1.0884438978193625
//     // 0.02057389781936237
//     //-0.00034754168959056595
//     return 0;
// }

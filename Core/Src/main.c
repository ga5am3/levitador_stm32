/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
// My includes
#include "string.h"
#include "usbd_cdc_if.h"
#include "stdlib.h"
#include "stdint.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM3_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */


#define WORD_LENGHT 32
#define INTEGER_BITS 10
#define FRACTIONAL_BITS 22

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

// Variables Kalman
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
    {-1 << FRACTIONAL_BITS, 0, 0},
    {0, -1 << FRACTIONAL_BITS, 0}
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

// Variables de comunicacion
char buffer[20];

// Variables para llenar en el callback
fixed_point_t x_hat_1[3][1];
fixed_point_t y_hat_negative[2][1];
fixed_point_t z_hat[2][1];
fixed_point_t lz[3][1];
fixed_point_t x_hat_result[3][1];

// Variables Fisicas
int h_prom = 35;


/// @brief Esta funcion se llama cuando cuando se detecta un flanco asendente en el
/// pin de señal de sensado de la camara. 
/// Cuando se ejecuta, se actualiza el valor de h_prom con el valor de la señal, y
/// se hace un toggle al PIN 13, (???) (que hace el pin 13?)
/// @param htim 
int captura = 0;
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim){
	h_prom = TIM3->CCR1;
  // I don't remember why this is here
  //	mayor a 2900 lo ignoro, sino actualizo el valor por los pixeles al final del sensor
	if (captura==0){
		if(h_prom>2900){
		    h_prom = h_prom;
		  }else{
		    h_prom = 2900;
		  }
			HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13); // What is this for??? A LED?
		captura = 1;
	}
}

fixed_point_t Kd[1][3] = {
  {
    FLOAT_TO_FIXED(0.0018029293079868),
    FLOAT_TO_FIXED(-0.4111538385920691),
    FLOAT_TO_FIXED(-0.0146874468496660)
  }
};
fixed_point_t h_ref = FLOAT_TO_FIXED(0.025f);
fixed_point_t precomp = FLOAT_TO_FIXED(-0.1662218623972525);
fixed_point_t u[1][1];

float i;
float u_float = 5.8;
float h; // Declare the variable h
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc){

	i = HAL_ADC_GetValue(&hadc1)*0.0023157-4.785;
	h = ((h_prom)*0.0272065-63.235847)*0.001; // valor en mm

	// x_0 = [i; h; 0]
	// x_hat[0][0] = FLOAT_TO_FIXED(i);
	// x_hat[1][0] = FLOAT_TO_FIXED(h);
	// x_hat[2][0] = FLOAT_TO_FIXED(0.0f);


  y[0][0] = FLOAT_TO_FIXED(i);
  y[1][0] = FLOAT_TO_FIXED(h);

	// Implementar el filtro de kalman
	// MATH
	// step 1: x_hat = G*x_hat + H*u
	// step 2: y_hat = C*x_hat
	// step 3: z_hat = y - y_hat
	// step 4: x_hat = x_hat + K*z_hat

	// Perform calculations
	// step 1: x_hat = G*x_hat + H*u
	fixed_point_t Gx_hat[3][1];
	fixed_point_t x_hat_1[3][1];
	matmul(3, 3, 1, G, x_hat, Gx_hat);
	// H*u = H_fixed * u_float
	fixed_point_t H_fixed_u[3][1] = {0}; // Initialize to zero
	H_fixed_u[0][0] = fixed_multiply(H_fixed[0][0], FLOAT_TO_FIXED(u_float));
	H_fixed_u[2][0] = fixed_multiply(H_fixed[0][2], FLOAT_TO_FIXED(u_float));


  //x_hat_1 = G x + H u
	vecadd(3, Gx_hat, H_fixed_u, x_hat_1);
	// step 2: y_hat = Cminus*x_hat
	//fixed_point_t y_hat_negative[2][1];
	matmul(2, 3, 1, Cminus, x_hat_1, y_hat_negative);
	// step 3: z_hat = y + y_hat_negative
	vecadd(2, y, y_hat_negative, z_hat);
	// step 4: x_hat = x_hat + K*z_hat
	matmul(3, 2, 1, Kkalman, z_hat, lz);
	vecadd(3, x_hat_1, lz, x_hat_result);
	// Save x_hat_result back to x_hat
	for (int i = 0; i < 3; i++) {
		x_hat[i][0] = x_hat_result[i][0];
	}
	// LQR
	// Kd = [0.018029293079868  -4.111538385920691  -0.146874468496660]
	// precomp = -1.662218623972525
	// step 1: u = -K*x + precomp * h_ref
  // u = -K*x + precomp * h_ref
  matmul(1, 3, 1, Kd, x_hat_result, u);
  u[0][0] = -u[0][0] + fixed_multiply(precomp, h_ref);
  u_float = - 1e3 * fixed_to_float(u[0][0]);
	// Use x_hat_result_float for further processing
	// convert u to the range of the PWM
	// Convert u to the range of the PWM, v_max = 12, v_min = 0
	// ARR = 7199
	// duty_cycle = CRR/ARR
	if(u_float < 0){
		u_float = 0;
	}else if(u_float > 12)
  {
		u_float = 12;
	}
		TIM1->CCR1 = (uint32_t)(u_float/12) * 7199; // 12 is max voltage, 7199 is ARR
		captura = 0;
	}

float h_hat;


static int direction = 1;
static int value = 0;
int value2 = 100;
int signal_1;
int signal_2;
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */
  HAL_ADC_Start_IT(&hadc1);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
  HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim1,TIM_CHANNEL_1);
  HAL_TIMEx_PWMN_Start(&htim1, TIM_CHANNEL_1);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  char data[35];

  while (1)
  {
    /* USER CODE END WHILE */
    h_hat = fixed_to_float(x_hat_result[1][0]);
//    sprintf(data, "%d %d %d",h_prom, (int)(10000*h), (int)(10000*h_hat)); // Test position and kalman
    //	CDC_Transmit_FS(data,strlen(data));
    //	HAL_Delay(100);
    // sprintf(data, "%d\n", h_prom);
    value += direction;
    value2 -= direction;
    if (value > 100) {
        value = 100;  // Constrain to max value
        direction = -1;  // Change direction
    } else if (value < 0) {
        value = 0;  // Constrain to min value
        direction = 1;  // Change direction
    }
    // signal_1 = (int)(h*1000);
    // signal_2 = (int)(h_hat*1000);
    HAL_Delay(100);
    sprintf(data, "%d|%d\n", value, value2);
    
    CDC_Transmit_FS(data, strlen(data));
    
    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC|RCC_PERIPHCLK_USB;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV6;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL_DIV1_5;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIGCONV_T3_TRGO;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 0;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 7199;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 3600;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_LOW;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 36;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 71;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 35;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_LOW;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */
  HAL_TIM_MspPostInit(&htim2);

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_IC_InitTypeDef sConfigIC = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 7199;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_IC_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
  sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
  sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
  sConfigIC.ICFilter = 15;
  if (HAL_TIM_IC_ConfigChannel(&htim3, &sConfigIC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 72;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */
  HAL_TIM_MspPostInit(&htim3);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

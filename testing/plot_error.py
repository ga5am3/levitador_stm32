import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('results_comp.csv')

# Group by 'frac' and calculate the mean of 'result_mse'
grouped_df = df.groupby('frac', as_index=False).mean()

# Extract the 'frac' and 'result_mse' columns from the grouped DataFrame
frac = grouped_df['frac']
result_mse = grouped_df['result_mse']

# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

# Plot the data on the first subplot
ax1.plot(frac, result_mse, marker='o')
ax1.set_xlabel('Fractional Bits (frac)')
ax1.set_ylabel('Mean Squared Error (result_mse)')
ax1.set_title('Mean Squared Error as a Function of Fractional Bits')
ax1.grid(True)

# Plot the data on the second subplot with log scale for the y-axis
ax2.plot(frac, result_mse, marker='o')
ax2.set_xlabel('Fractional Bits (frac)')
ax2.set_ylabel('Mean Squared Error (result_mse)')
ax2.set_title('Mean Squared Error as a Function of Fractional Bits (Log Scale)')
ax2.set_yscale('log')
ax2.grid(True)


# Show the plot
plt.savefig('mse_plot.png')
plt.tight_layout()
plt.show()
import pandas as pd

# Load the two CSV files
file1 = 'Full rephrased - Approach 5 (2).csv'  # Replace with your file path
file2 = 'customer_service_issues106 - customer_service_issues106.csv'  # Replace with your file path

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Merge the two dataframes on both 'issue' and 'user' columns
merged_df = pd.merge(df1, df2, on=['issue', 'user'])

# Save the merged result into a new CSV file
merged_df.to_csv('merged_output.csv', index=False)

print("Merge complete. Merged file saved as 'merged_output.csv'")

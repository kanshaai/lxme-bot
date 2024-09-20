import pandas as pd

# Load the original CSV file
original_csv_path = 'customer_service_issues08 - customer_service_issues08 (1).csv'
df = pd.read_csv(original_csv_path)

# Group by 'theme' and aggregate unique 'issue'
grouped_df = df.groupby('theme')['issue'].unique().reset_index()

# Create a new DataFrame to hold the formatted data
formatted_data = []

# Populate the formatted data
for index, row in grouped_df.iterrows():
    theme = row['theme']
    issues = row['issue']
    
    # Add a row for the theme
    formatted_data.append([theme, ''])  # Theme row
    
    # Add a row for each unique issue under the theme
    for issue in issues:
        formatted_data.append(['', issue])

# Convert the formatted data to a DataFrame
formatted_df = pd.DataFrame(formatted_data, columns=['theme', 'issue'])

# Save the result to a new CSV file
grouped_csv_path = 'grouped_issues_by_theme.csv'
formatted_df.to_csv(grouped_csv_path, index=False)

print(f'Grouped themes and unique issues have been saved to {grouped_csv_path}')

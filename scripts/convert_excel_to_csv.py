import pandas as pd
import os

excel_file = 'data/RetailStores.xlsx'
output_dir = 'data'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define the sheets and their corresponding CSV names
sheets_to_csv = {
    'Set I': 'RetailStores.xlsx - Set I.csv',
    'Set J': 'RetailStores.xlsx - Set J.csv',
    'Set M': 'RetailStores.xlsx - Set M.csv',
    'Set S': 'RetailStores.xlsx - Set S.csv',
    'h_is': 'RetailStores.xlsx - h_is.csv',
    'd_ij': 'RetailStores.xlsx - d_ij.csv',
    'V_j=0': 'RetailStores.xlsx - V_j=0.csv',
}

try:
    for sheet_name, csv_name in sheets_to_csv.items():
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.to_csv(os.path.join(output_dir, csv_name), index=False, header=True)
        print(f"Converted sheet '{sheet_name}' to '{csv_name}'")
    print("All specified sheets converted to CSV successfully!")
except FileNotFoundError:
    print(f"Error: The file '{excel_file}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

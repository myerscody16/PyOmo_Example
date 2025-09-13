import pandas as pd
import os

excel_file = 'data/RetailStores.xlsx'
output_dir = 'data'

os.makedirs(output_dir, exist_ok=True)
sheets_to_csv = {
    'Set I': 'RetailStores-Set I.csv',
    'Set J': 'RetailStores-Set J.csv',
    'Set M': 'RetailStores-Set M.csv',
    'Set S': 'RetailStores-Set S.csv',
    'h_is': 'RetailStores-h_is.csv',
    'd_ij': 'RetailStores-d_ij.csv',
    'V_j=0': 'RetailStores-V_j=0.csv',
}

for sheet_name, csv_name in sheets_to_csv.items():
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df.to_csv(os.path.join(output_dir, csv_name), index=False, header=True)
    print(f"Converted sheet '{sheet_name}' to '{csv_name}'")
print("All specified sheets converted to CSV successfully")

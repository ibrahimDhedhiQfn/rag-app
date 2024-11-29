import pandas as pd

# File paths
input_file = "shopify_products.csv"  # Replace with your CSV file path
output_file = "cleaned_shopify_products.csv"

# Read the CSV file
try:
    data = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"File {input_file} not found.")
    exit()

# Drop duplicates
data.drop_duplicates(inplace=True)

# Required fields: Ensure 'Handle' and 'Title' are not missing
required_fields = ['Handle', 'Title']
for field in required_fields:
    if field in data.columns:
        data = data[~data[field].isnull()]
    else:
        print(f"Required field '{field}' is missing in the input file.")
        exit()

# Handle missing values for optional fields
# Fill numerical columns with 0
numerical_columns = ['Variant Grams', 'Variant Inventory Qty', 'Variant Price', 'Variant Compare At Price']
for col in numerical_columns:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

# Fill text columns with empty strings
text_columns = [col for col in data.columns if col not in numerical_columns]
for col in text_columns:
    if col in data.columns:
        data[col] = data[col].fillna("").str.strip()

# Validate numerical columns for negative values
for col in ['Variant Grams', 'Variant Price', 'Variant Inventory Qty']:
    if col in data.columns:
        data[col] = data[col].apply(lambda x: max(x, 0))

# Ensure 'Tags' column is properly formatted
if 'Tags' in data.columns:
    data['Tags'] = data['Tags'].str.replace(",", ", ")

# Save the cleaned data
data.to_csv(output_file, index=False)
print(f"Cleaned data saved to {output_file}")

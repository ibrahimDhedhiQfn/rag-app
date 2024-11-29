import pandas as pd
import json

# File paths
input_file = "shopify_products.csv"  # Replace with your CSV file path
output_file = "shopify_product_faq.json"

# Read the CSV file
try:
    data = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"File {input_file} not found.")
    exit()

# Drop rows with missing critical data
data.dropna(subset=['Handle', 'Title', 'Variant Price'], inplace=True)

# Generate questions and answers
faq_list = []

for _, row in data.iterrows():
    # Basic product-related questions
    faq_list.append({
        "question": f"What is the price of {row['Title']}?",
        "answer": f"The price of {row['Title']} is ${row['Variant Price']}."
    })
    
    faq_list.append({
        "question": f"Is {row['Title']} available in stock?",
        "answer": f"We currently have {row['Variant Inventory Qty']} units of {row['Title']} available."
    })
    
    faq_list.append({
        "question": f"What type of product is {row['Title']}?",
        "answer": f"{row['Title']} is a {row['Type']}."
    })
    
    if pd.notna(row.get('Tags')):
        faq_list.append({
            "question": f"What are the tags associated with {row['Title']}?",
            "answer": f"The tags for {row['Title']} are: {row['Tags']}."
        })
    
    if pd.notna(row.get('Image Src')):
        faq_list.append({
            "question": f"Where can I see an image of {row['Title']}?",
            "answer": f"You can view an image of {row['Title']} at {row['Image Src']}."
        })

# Save to JSON file
with open(output_file, "w") as json_file:
    json.dump(faq_list, json_file, indent=4)

print(f"FAQ JSON file saved to {output_file}")

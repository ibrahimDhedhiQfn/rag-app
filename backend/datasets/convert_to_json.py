from flask import Flask, request, jsonify
import json
from sentence_transformers import SentenceTransformer
import faiss

app = Flask(__name__)

def generate_embeddings():
    try:
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load dataset
        with open('../datasets/faq_data.json', 'r') as f:
            data = json.load(f)

        # Create embeddings
        texts = [f"Question: {item['question']} Answer: {item['answer']}" for item in data]
        embeddings = model.encode(texts)

        # Create FAISS index
        index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 similarity
        index.add(embeddings)

        # Save FAISS index
        faiss.write_index(index, '../datasets/index.faiss')

        # Save metadata
        with open('../datasets/data.json', 'w') as f:
            json.dump(data, f)

        print("Embeddings and index saved successfully!")
        return {"status": "success", "message": "Embeddings and index created."}
    except Exception as e:
        print(f"Error in generating embeddings: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/generate_faq', methods=['POST'])
def generate_faq():
    try:
        # Get the incoming JSON data
        products = request.get_json()
        if not products:
            return jsonify({"error": "No data received"}), 400

        faq_list = []

        for product in products:
            title = product.get("title", "Unknown Product")
            
            # Safely handle variants
            variant_edges = product.get("variants", {}).get("edges", [])
            price = variant_edges[0].get("node", {}).get("price", "N/A") if variant_edges else "N/A"
            inventory_quantity = variant_edges[0].get("node", {}).get("inventoryQuantity", "N/A") if variant_edges else "N/A"
            
            product_type = product.get("productType", "Unknown Type")
            tags = ", ".join(product.get("tags", [])) if product.get("tags") else "No tags available"
            
            # Safely handle images
            image_edges = product.get("images", {}).get("edges", [])
            image_url = image_edges[0].get("node", {}).get("src", "No image available") if image_edges else "No image available"
            
            # Generate FAQs for the product
            faq_list.extend([
                {
                    "question": f"What is the price of {title}?",
                    "answer": f"The price of {title} is ${price}."
                },
                {
                    "question": f"Is {title} available in stock?",
                    "answer": f"We currently have {inventory_quantity} units of {title} available."
                },
                {
                    "question": f"What type of product is {title}?",
                    "answer": f"{title} is a {product_type}."
                },
                {
                    "question": f"What are the tags associated with {title}?",
                    "answer": f"The tags for {title} are: {tags}."
                },
                {
                    "question": f"Where can I see an image of {title}?",
                    "answer": f"You can view an image of {title} at {image_url}."
                }
            ])

        # Save the generated FAQ list to a JSON file
        json_file_path = '../datasets/faq_data.json'
        with open(json_file_path, 'w') as f:
            json.dump(faq_list, f, indent=4)

        # Generate embeddings and FAISS index
        embedding_result = generate_embeddings()

        return jsonify({
            "message": "FAQ generation completed and saved.",
            "embedding_status": embedding_result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

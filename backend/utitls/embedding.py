from sentence_transformers import SentenceTransformer
import faiss
import json

def generate_embeddings():
    # Load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load dataset
    with open('..\datasets\shopify_product_faq.json', 'r') as f:
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

if __name__ == "__main__":
    generate_embeddings()

import json
import os
import chromadb

def build_vector_database(json_path, db_path):
    print("Initializing Local Vector Database...")
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}")
        return None

    # 1. Load our extracted JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        document_data = json.load(f)
        
    # 2. Set up ChromaDB to save directly to your hard drive
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    
    # 3. Create a collection (Think of this like a table in SQL)
    collection = client.get_or_create_collection(name="infrastructure_codes")
    
    documents = []
    metadatas = []
    ids = []
    
    print(f"Scanning {len(document_data)} pages for insertion...")

    for item in document_data:
        page_num = item["page_number"]
        content = item["content"]
        
        # We don't want to embed blank pages or API errors
        if "SKIP_PAGE" in content or "Error" in content:
            continue
            
        documents.append(content)
        metadatas.append({"page_number": page_num})
        ids.append(f"page_{page_num}")
        
    if not documents:
        print("No valid documents found to embed!")
        return None

    # 4. Insert into the database. 
    # Chroma automatically downloads a tiny, local AI model to convert your text to numbers!
    print(f"Embedding {len(documents)} pages... (This takes a few seconds)")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Success! Vector database built and saved to {db_path}")
    return collection

if __name__ == "__main__":
    JSON_PATH = "data/processed/vlm_extracted_data.json"
    
    # We will save the database locally in our data folder
    DB_PATH = "data/chroma_db"
    
    # Build the database
    my_collection = build_vector_database(JSON_PATH, DB_PATH)
    
    # --- THE MAGIC TEST ---
    if my_collection:
        print("\n--- Running a Semantic Search Test ---")
        
        # We are asking a question in plain English, not exact keywords
        test_query = "What are the codes for green buildings or energy conservation?"
        print(f"Question: '{test_query}'\n")
        
        # Search the database for the top 2 most mathematically relevant pages
        results = my_collection.query(
            query_texts=[test_query],
            n_results=2 
        )
        
        for i in range(len(results['documents'][0])):
            page = results['metadatas'][0][i]['page_number']
            # Grab just the first 250 characters of the page so we don't flood the terminal
            snippet = results['documents'][0][i][:250] 
            
            print(f"Rank {i+1} Match | Found on Page {page}")
            print(f"Snippet: {snippet}...\n")
import os
import chromadb
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Paste your Google API Key here
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)

# We use Gemini 2.5 Flash for the conversational reasoning
model = genai.GenerativeModel('gemini-2.5-flash')

# Connect to our local Chroma Database
DB_PATH = "data/chroma_db"
if not os.path.exists(DB_PATH):
    print("Error: Vector database not found. Did you run Phase 3?")
    exit()

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name="infrastructure_codes")

# --- 2. THE CORE RAG ENGINE ---
def ask_infrastructure_bot(user_question):
    print("\n[Searching database for relevant structural codes...]")
    
    # Step 1: RETRIEVE the top 3 most relevant pages
    results = collection.query(
        query_texts=[user_question],
        n_results=3 
    )
    
    # Step 2: AUGMENT the context
    context_block = ""
    sources = []
    
    for i, doc in enumerate(results['documents'][0]):
        page_num = results['metadatas'][0][i]['page_number']
        sources.append(str(page_num))
        context_block += f"\n--- DATA FROM PAGE {page_num} ---\n{doc}\n"
        
    # --- ADD THIS DEBUG BLOCK ---
    print("\n" + "*"*40)
    print("🔍 DEBUG: WHAT CHROMA DB FOUND:")
    print(context_block[:600] + "\n... [truncated]")
    print("*"*40 + "\n")
        
    # The System Prompt: We enforce strict guardrails so it acts like a senior engineer
    # and doesn't hallucinate fake building codes.
    augmented_prompt = f"""You are a Senior Structural Engineering Assistant. 
    Your job is to answer the user's question using ONLY the provided Context from the official infrastructure codes.
    
    If the answer is not contained in the Context, do not guess. Simply reply: "I cannot find the exact specifications for this in the provided manual pages."
    
    Context:
    {context_block}
    
    User Question:
    {user_question}
    """
    
    print("[Analyzing retrieved data and generating response...]\n")
    
    # Step 3: GENERATE the answer using Gemini
    try:
        response = model.generate_content(augmented_prompt)
        
        # Print the final output clearly with source citations
        print("==================================================")
        print(f"🤖 AI ENGINEER RESPONSE:\n")
        print(response.text.strip())
        print(f"\n📚 Sources referenced: Pages {', '.join(sources)}")
        print("==================================================")
        
    except Exception as e:
        print(f"Error generating response: {e}")


# --- 3. THE INTERACTIVE TERMINAL LOOP ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏗️ INFRASTRUCTURE RAG SYSTEM INITIALIZED")
    print("Type 'exit' or 'quit' to shut down the engine.")
    print("="*50 + "\n")
    
    while True:
        question = input("\n👨‍💻 Ask a question about the codes: ")
        
        if question.lower() in ['exit', 'quit']:
            print("Shutting down the RAG engine. Goodbye!")
            break
            
        if not question.strip():
            continue
            
        ask_infrastructure_bot(question)
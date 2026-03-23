import streamlit as st
import chromadb
import google.generativeai as genai
import os

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Infrastructure RAG", page_icon="🏗️", layout="centered")
st.title("🏗️ Infrastructure Codes AI")
st.caption("Ask questions based on the extracted IS Code Manual.")

# Paste your API Key here
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. LOAD DATABASE ---
# We use @st.cache_resource so it doesn't reload the database every time you type a letter
@st.cache_resource
def load_database():
    db_path = "data/chroma_db"
    if not os.path.exists(db_path):
        return None
    client = chromadb.PersistentClient(path=db_path)
    return client.get_collection(name="infrastructure_codes")

collection = load_database()

if not collection:
    st.error("Vector database not found! Please run the Phase 3 script first.")
    st.stop()

# --- 3. CHAT INTERFACE ---
# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. RAG LOGIC ---
# This creates the chat input box at the bottom of the screen
if prompt := st.chat_input("Ask a question about the structural codes..."):
    
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show AI response with a loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Searching manuals and generating response..."):
            
            # Step 1: RETRIEVE
            results = collection.query(query_texts=[prompt], n_results=3)
            
            # Step 2: AUGMENT
            context_block = ""
            sources = []
            image_paths_to_show = [] # NEW: List to hold the images we want to show
            
            for i, doc in enumerate(results['documents'][0]):
                page_num = results['metadatas'][0][i]['page_number']
                sources.append(str(page_num))
                context_block += f"\n--- DATA FROM PAGE {page_num} ---\n{doc}\n"
                
                # NEW: Construct the path to the original high-res image
                img_path = f"data/processed/document_pages/page_{page_num}.png"
                if os.path.exists(img_path) and img_path not in image_paths_to_show:
                    image_paths_to_show.append(img_path)
            
            augmented_prompt = f"""You are a Senior Structural Engineering Assistant. 
            Answer the user's question using ONLY the provided Context from the official infrastructure codes.
            If the answer is not contained in the Context, do not guess. Simply reply: "I cannot find the exact specifications for this in the provided manual pages."
            
            Context:
            {context_block}
            
            User Question:
            {prompt}
            """
            
            # Step 3: GENERATE
            try:
                response = model.generate_content(augmented_prompt)
                answer = response.text.strip()
                
                full_response = f"{answer}\n\n---\n*📚 Sources referenced: Pages {', '.join(sources)}*"
                
                # 1. Print the text to the UI
                st.markdown(full_response)
                
                # 2. NEW: Display the original source pages in a clean, collapsible expander!
                if image_paths_to_show:
                    with st.expander("🖼️ View Original Source Pages"):
                        for img_path in image_paths_to_show:
                            st.image(img_path, caption=f"Source Document: {os.path.basename(img_path)}", use_container_width=True)
                
                # 3. Save everything to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
#  Infrastructure Codes AI: Multimodal RAG Pipeline

An end-to-end Retrieval-Augmented Generation (RAG) system designed to extract, embed, and query complex structural engineering manuals and IS Codes. 

This project tackles the challenge of parsing highly technical, unstructured PDFs—including dense text, tables, and structural schematics—and makes them instantly searchable through a localized AI agent with a side-by-side document verification UI.

##  Key Features

* **Multimodal Data Extraction:** Utilizes Google's Gemini Vision AI to read raw PDF pages, accurately extracting text while intelligently interpreting complex engineering diagrams and tabular data.
* **Resilient ETL Pipeline:** Engineered with "Smart Resume" state management, exponential backoff, and image downscaling (token starvation) to process massive datasets while strictly adhering to Cloud API rate limits.
* **Semantic Vector Search:** Implements ChromaDB for entirely local, lightning-fast semantic retrieval of engineering specifications.
* **Side-by-Side Verification UI:** Built with Streamlit, the application features a split-screen interface. The AI assistant provides answers on the left, while instantly pulling up the original, high-resolution source diagrams on the right for zero-hallucination verification.

##  System Architecture

1. **Phase 1: Preprocessing** - Raw PDF manuals are split into high-resolution PNGs.
2. **Phase 2: Vision Extraction** - Images are optimized and passed to the VLM (Vision-Language Model) to generate structured markdown text.
3. **Phase 3: Embedding** - The structured text is chunked, converted into mathematical vectors, and stored locally in ChromaDB.
4. **Phase 4: Retrieval & Generation** - User queries pull the top matching documents, which are passed to the LLM alongside the user prompt to generate highly accurate, context-aware answers.

##  Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/Ayan-spec347/Structural-rag-agent.git](https://github.com/Ayan-spec347/Structural-rag-agent.git)
cd Structural-rag-agent

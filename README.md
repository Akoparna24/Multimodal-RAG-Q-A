---
title: Multimodal RAG QA
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
---

# 🔍 Multimodal RAG — Visual Document Q&A

A production-ready RAG (Retrieval Augmented Generation) system that goes beyond plain text — it understands **tables, charts, diagrams, and images** inside PDF documents.

Ask questions like:
- *"What does the revenue chart show?"*
- *"Extract the data from the financial table on page 5"*
- *"What machines are shown in the document?"*

---

## 🧠 What Makes This Unique

Most RAG systems only read text. This system handles **all content types**:

| Content Type | Standard RAG | This System |
|---|---|---|
| Plain Text | ✅ | ✅ |
| Tables | ⚠️ Often garbled | ✅ Structured extraction |
| Charts & Graphs | ❌ Invisible | ✅ Vision AI describes them |
| Diagrams | ❌ Skipped | ✅ Vision AI describes them |
| Multiple PDFs | ❌ | ✅ Search across all |

---

## 🏗️ Architecture

```
PDF Document
     │
     ▼
┌─────────────────────┐
│  PyMuPDF +          │  ← Extracts text, tables, images
│  pdfplumber         │    separately from each page
└────────┬────────────┘
         │
   ┌─────┴──────┐
   │            │
   ▼            ▼
Text/Tables   Images
   │            │
   │            ▼
   │   ┌─────────────────┐
   │   │  Groq Vision    │  ← Llama 4 Scout describes
   │   │  (LLaVA)        │    charts, diagrams, figures
   │   └────────┬────────┘
   │            │
   └─────┬──────┘
         ▼
┌─────────────────────┐
│  ChromaDB           │  ← Stores embeddings using
│  + sentence-        │    all-MiniLM-L6-v2 (local)
│  transformers       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Groq Llama3        │  ← Generates grounded answers
│  (llama-3.1-8b)     │    from retrieved chunks
└─────────┬───────────┘
          │
          ▼
     Gradio UI
```

---

## 🛠️ Tech Stack

| Component | Tool | Why |
|---|---|---|
| PDF Parsing | PyMuPDF + pdfplumber | Pure Python, no system dependencies |
| Vision AI | Groq Vision (Llama 4 Scout) | Free, fast, accurate image description |
| Text LLM | Groq (Llama 3.1 8B) | Free, fast inference |
| Embeddings | sentence-transformers | Free, runs locally on CPU |
| Vector Store | ChromaDB | Free, persistent, no setup needed |
| UI | Gradio | Simple, deployable on Hugging Face |

**100% Free — No paid APIs required**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### Installation

```bash
# Clone the repo
git clone https://github.com/Akoparna24/Multimodal-RAG-Q-A.git
cd Multimodal-RAG-Q-A

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Setup API Keys

Create a `.env` file in the root folder:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: https://console.groq.com

### Run the App

```bash
python app.py
```

Open **http://localhost:7860** in your browser.

---

## 📖 How to Use

1. **Upload** one or more PDF documents
2. Click **"Process Document"** and wait for indexing
3. **Ask questions** about anything in the document — text, tables, charts, images

### Example Questions
- *"What was the revenue in FY 23-24?"*
- *"Summarise the financial highlights"*
- *"What does the bar chart on page 5 show?"*
- *"Who is the Chief Financial Officer?"*
- *"What machines are shown in the document?"*

---

## 📁 Project Structure

```
multimodal_rag/
├── src/
│   ├── ingestion.py      # PDF parsing — text, tables, images
│   ├── vision.py         # Groq Vision image description
│   ├── vectorstore.py    # ChromaDB embedding + retrieval
│   └── rag_chain.py      # RAG pipeline — retrieve + generate
├── app.py                # Gradio web UI
├── requirements.txt      # Python dependencies
└── .env                  # API keys (not uploaded to GitHub)
```

---

## 🔑 Key Features

- **Multimodal understanding** — text, tables, charts, and diagrams all searchable
- **Smart image description** — Groq Vision generates rich descriptions of visual content
- **Multi-document support** — upload and query multiple PDFs simultaneously
- **Duplicate detection** — already indexed documents are not re-processed
- **Parallel vision processing** — images described concurrently for speed
- **Source attribution** — answers include page numbers for verification
- **Fully local embeddings** — sentence-transformers runs on CPU, no GPU needed

---

## 🎯 Technical Highlights

- Built an end-to-end **multimodal RAG pipeline** handling text, tables, and visual content
- Integrated **vision-language models** (Groq Vision/Llama 4 Scout) to make images semantically searchable
- Implemented **parallel API calls** with ThreadPoolExecutor for faster image processing
- Designed **source-filtered retrieval** enabling multi-document Q&A without context pollution
- Used **ChromaDB with cosine similarity** and sentence-transformers for semantic search
- Built a **production-ready Gradio UI** with input validation and smart state management

---

## 🌐 Deployment

This app is designed to deploy on **Hugging Face Spaces** for free.

1. Push this repo to GitHub
2. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
3. Create a new Space → select **Gradio**
4. Connect your GitHub repo
5. Add `GROQ_API_KEY` as a secret in Space settings

---

## 📄 License

MIT License — free to use and modify.

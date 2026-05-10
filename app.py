import os
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv

from src.ingestion import parse_document
from src.vision import enrich_images
from src.vector_store import get_vectorstore, add_elements, search, is_document_indexed
from src.rag_chain import answer_question

load_dotenv()

# Global vector store
collection = get_vectorstore()

def upload_document(files):
    """Handle multiple document uploads and indexing."""
    if not files:
        return "Please upload at least one PDF file."

    # files is now a list
    if not isinstance(files, list):
        files = [files]

    results = []
    for file in files:
        filename = Path(file.name).name
        if is_document_indexed(collection, filename):
            results.append(f"{filename} — already indexed")
            continue
        try:
            elements = parse_document(file.name)
            elements = enrich_images(elements)
            count    = add_elements(collection, elements)
            results.append(f"{filename} — indexed {count} chunks")
        except Exception as e:
            results.append(f"{filename} — error: {e}")

    return "\n".join(results)

def ask_question(question, filenames, history):
    if not question.strip():
        return history, ""

    greetings = ["hi", "hello", "hey", "how are you", "good morning", "good evening"]
    if question.strip().lower() in greetings:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": "Hi! I'm your document assistant. Ask me anything about your uploaded documents!"})
        return history, ""

    if not filenames:
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": "Please upload and process a document first."})
        return history, ""

    # Search across all uploaded files
    all_chunks = []
    for filename in filenames.split(","):
        if not is_document_indexed(collection, filename.strip()):
            continue
        chunks = search(collection, question, filename.strip())
        all_chunks.extend(chunks)

    # Sort by score and take top 5
    all_chunks = sorted(all_chunks, key=lambda x: x["score"], reverse=True)[:5]

    answer = answer_question(question, all_chunks)

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    return history, ""

with gr.Blocks(title="Multimodal RAG") as demo:

    gr.Markdown("# Multimodal Document Q&A")
    gr.Markdown("Upload a PDF and ask questions about text, tables, charts and images.")

    with gr.Row():

        # Left panel — upload
        with gr.Column(scale=1):
            gr.Markdown("### Step 1 — Upload Document")
            file_input = gr.File(
                label="Upload PDFs",
                file_types=[".pdf"],
                file_count="multiple"
            )
            upload_btn   = gr.Button("Process Document", variant="primary")
            upload_status = gr.Textbox(label="Status", interactive=False)
            filename_state = gr.State("")

        # Right panel — chat
        with gr.Column(scale=2):
            gr.Markdown("### Step 2 — Ask Questions")
            chatbot  = gr.Chatbot(height=400)
            question = gr.Textbox(placeholder="Ask anything about your document...")
            ask_btn = gr.Button("Ask", variant="primary", interactive=False)

    # Wire up events
    def process_file(files):
        if not files:
            return "Please upload a PDF file.", "", gr.update(interactive=False)

        if not isinstance(files, list):
            files = [files]

        status = upload_document(files)
        filenames = ",".join([Path(f.name).name for f in files])
        return status, filenames, gr.update(interactive=True)


    upload_btn.click(
        fn=process_file,
        inputs=[file_input],
        outputs=[upload_status, filename_state, ask_btn]
    )

    ask_btn.click(
        fn=ask_question,
        inputs=[question, filename_state, chatbot],
        outputs=[chatbot, question]
    )

    question.submit(
        fn=ask_question,
        inputs=[question, filename_state, chatbot],
        outputs=[chatbot, question]
    )

if __name__ == "__main__":
    demo.launch()
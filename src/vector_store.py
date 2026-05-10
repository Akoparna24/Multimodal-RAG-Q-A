import chromadb
from chromadb.utils import embedding_functions
from rich.console import Console
import uuid

console = Console()

EMBED_MODEL = "all-MiniLM-L6-v2"

def get_vectorstore(persist_dir: str = "data/chroma_db"):
    """Create or load a ChromaDB vector store."""
    console.print(f"Loading embedding model: {EMBED_MODEL}")

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    client = chromadb.PersistentClient(path=persist_dir)

    collection = client.get_or_create_collection(
        name="multimodal_rag",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    console.print(f"Vector store ready — {collection.count()} existing chunks")
    return collection

def add_elements(collection, elements: list[dict]) -> int:
    """Embed and store all elements in ChromaDB."""
    documents = []
    metadatas = []
    ids = []

    for element in elements:
        content = element.get("content", "").strip()

        # Skip empty elements
        if not content:
            continue

        metadata = {
            "type":       element["type"],
            "page":       element.get("page", 0),
            "source":     element.get("source", ""),
            "image_path": element.get("image_path", ""),
        }

        documents.append(content)
        metadatas.append(metadata)
        ids.append(str(uuid.uuid4()))

    # Add to ChromaDB in batches
    batch_size = 50
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size],
        )

    console.print(f"Indexed {len(documents)} chunks successfully")
    return len(documents)

def search(collection, query: str, filename: str, n_results: int = 5) -> list[dict]:
    """Search for relevant chunks from a specific document."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"source": filename}
    )

    formatted = []
    for i, doc in enumerate(results["documents"][0]):
        meta  = results["metadatas"][0][i]
        score = round(1 - results["distances"][0][i], 4)

        formatted.append({
            "content":    doc,
            "type":       meta.get("type", ""),
            "page":       meta.get("page", 0),
            "source":     meta.get("source", ""),
            "image_path": meta.get("image_path", ""),
            "score":      score,
        })

    return formatted

def is_document_indexed(collection, filename: str) -> bool:
    """Check if a specific document is already indexed."""
    results = collection.get(where={"source": filename})
    return len(results["ids"]) > 0

def clear_vectorstore(persist_dir: str = "data/chroma_db"):
    """Delete all existing data in the vector store."""
    import shutil
    shutil.rmtree(persist_dir, ignore_errors=True)
    console.print("Vector store cleared!")
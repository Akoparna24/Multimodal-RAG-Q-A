import fitz  # -----> this is PyMuPDF's import name, used for extracting text and images from PDF
import pdfplumber  # -----> used specifically for extracting tables
import base64  # -----> converts images to base64 string for sending to Groq Vision
from pathlib import Path  # -----> handles file paths cleanly across Windows/Mac/Linux
from rich.console import Console  # ----->  colored terminal output

console = Console()

def extract_text(pdf_path: str) -> list[dict]:
    """Extract text blocks from each page of the PDF."""
    results = []
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            results.append({
                "type": "text",
                "content": text,
                "page": page_num,
                "source": Path(pdf_path).name
            })

    console.print(f"[green]Extracted text from {len(results)} pages[/green]")
    return results

def extract_tables(pdf_path: str) -> list[dict]:
    """Extract tables from each page of the PDF."""
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                if not table:
                    continue

                # Convert table to readable text format
                table_text = ""
                for row in table:
                    # Clean None values
                    cleaned_row = [cell if cell else "" for cell in row]
                    table_text += " | ".join(cleaned_row) + "\n"

                if table_text.strip():
                    results.append({
                        "type": "table",
                        "content": table_text,
                        "page": page_num,
                        "source": Path(pdf_path).name
                    })

    console.print(f"Extracted {len(results)} tables")
    return results

def extract_images(pdf_path: str, output_dir: str = "data/processed/images") -> list[dict]:
    """Extract images from each page of the PDF."""
    results = []
    images_dir = Path(output_dir)
    images_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, start=1):
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Skip tiny images — likely decorative
            if len(image_bytes) < 5000:
                continue

            # Save image to disk
            image_filename = f"page{page_num}_img{img_index}.{image_ext}"
            image_path = images_dir / image_filename

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Convert to base64 for vision model
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            results.append({
                "type": "image",
                "content": "",
                "page": page_num,
                "source": Path(pdf_path).name,
                "image_path": str(image_path),
                "image_base64": image_base64,
                "image_ext": image_ext
            })

    console.print(f"Extracted {len(results)} meaningful images")
    return results


def parse_document(pdf_path: str) -> list[dict]:
    """Parse a PDF and extract all text, tables and images."""
    console.print(f"Parsing: {Path(pdf_path).name}")

    text_elements = extract_text(pdf_path)
    table_elements = extract_tables(pdf_path)
    image_elements = extract_images(pdf_path)

    all_elements = text_elements + table_elements + image_elements

    console.print(f"Total elements: {len(all_elements)}")
    return all_elements
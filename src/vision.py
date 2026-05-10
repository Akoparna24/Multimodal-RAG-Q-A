import os
import base64
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

PROMPT = """Describe this image in detail for a search index. Include:
- What type of visual it is (chart, table, diagram, photo etc.)
- All visible text and numbers
- Key data points if it is a chart or graph
- Any trends or patterns you notice
Be thorough — this description will be used to answer questions."""

def describe_image(image_base64: str, image_ext: str = "jpeg") -> str:
    """Send an image to Groq Vision and get a text description."""
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_ext};base64,{image_base64}"
                        }
                    }
                ]
            }],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        console.print(f"[red]Vision error: {e}[/red]")
        return ""

import concurrent.futures

def enrich_images(elements: list[dict], max_images: int = 10) -> list[dict]:
    """Describe images in parallel using Groq Vision."""
    image_elements = [e for e in elements if e["type"] == "image"]
    image_elements = image_elements[:max_images]
    total = len(image_elements)

    console.print(f"Describing {total} images in parallel with Groq Vision...")

    def describe_element(element):
        description = describe_image(
            image_base64=element["image_base64"],
            image_ext=element.get("image_ext", "jpeg")
        )
        element["content"] = description
        return element

    # Process images in parallel with 5 workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(describe_element, el): el for el in image_elements}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            console.print(f"  Image {i}/{total} done")
            future.result()

    console.print("Vision enrichment complete!")
    return elements
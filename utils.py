import os
import uuid
import wget
import base64
import pdfplumber
import PyPDF2
from PIL import Image


def load_images(inputs: dict) -> dict:
    """Load images from a directory and encode them as base64."""
    images_encoded = []
    images_path = inputs["images_path"]
    for file_name in os.listdir(images_path):
        full_path = os.path.join(images_path, file_name)
        if os.path.isfile(full_path) and file_name.lower().endswith(
            (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        ):
            with open(full_path, "rb") as image_file:
                base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
                images_encoded.append(base64_encoded)

    return {"encoded_images": images_encoded}


def extract_tables_from_pdf(pdf_path: str) -> list:
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception as e:
        return {"error": str(e)}
    return tables


def fix_text_encoding(text: str) -> str:
    replacements = {
        "â€™": "’",
        "â€œ": "“",
        "â€": "”",
        "â€¢": "•",
        "â€“": "–",
        "â€”": "—",
        "â€˜": "‘",
        "Â": " ",
        "â€™": "’",
        "â€¢": "•",
        "â€“": "–",
        "â€”": "—",
        "â€˜": "‘",
        "â€¦": "…",
        "â€": "”",
        "â€œ": "“",
        "â€": '"',
        "â€™": "'",
        "â€": '"',
        "â€¢": "•",
        "â€“": "–",
        "â€”": "—",
        "â„¢": "™",
        "âˆš": "√",
    }
    for bad_char, good_char in replacements.items():
        text = text.replace(bad_char, good_char)
    return text


def extract_text_with_pdfplumber(pdf_path: str) -> str:
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(fix_text_encoding(text))
    return "\n".join(all_text)


def download_pdf_and_convert_to_images(url: str) -> dict:
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")

    try:
        # Downloading the PDF file
        filename = wget.download(url, out="Downloads/")
        folder_uuid = str(uuid.uuid4())
        images_folder_path = os.path.join("Downloads", folder_uuid)
        os.makedirs(images_folder_path)

        # Extracting text
        pdfplumber_text = extract_text_with_pdfplumber(filename)

        # Opening and processing the PDF for images
        with pdfplumber.open(filename) as pdf:
            for page_number, page in enumerate(pdf.pages):
                # Converting page to image
                page_image = page.to_image(
                    resolution=300
                )  # Higher DPI for better quality
                original = page_image.original
                if original.mode != "RGB":
                    original = original.convert("RGB")

                image_path = os.path.join(images_folder_path, f"{uuid.uuid4()}.jpg")
                original.save(image_path, "JPEG", quality=95)
        extracted_tables = extract_tables_from_pdf(filename)

        return {
            "pdf_text": pdfplumber_text,
            "images_path": images_folder_path,
            "tables_data": extracted_tables,
        }
    except Exception as e:
        print(e)
        return {"error": str(e)}


def get_column_value(row, column_name):
    if column_name in row:
        return row[column_name]
    else:
        print(f"Column {column_name} not found in the data.")
        return None  # Or appropriate fallback value

def get_column_value_from_ws(row, col_name, ws):
    col_name = col_name.strip()  # Strip whitespace from the column name being searched
    for cell in ws[1]:  # assuming the first row is the header
        if cell.value and cell.value.strip() == col_name:
            return row[cell.column - 1].value
    return None
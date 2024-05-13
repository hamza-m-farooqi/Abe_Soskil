import os
import uuid
import wget
import base64
import pdfplumber
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


def download_pdf_and_convert_to_images(url: str) -> dict:
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")

    try:
        # Downloading the PDF file
        filename = wget.download(url, out="Downloads/")
        all_text = []
        folder_uuid = str(uuid.uuid4())
        images_folder_path = os.path.join("Downloads", folder_uuid)
        os.makedirs(images_folder_path)

        # Opening and processing the PDF
        with pdfplumber.open(filename) as pdf:
            for page_number, page in enumerate(pdf.pages):
                # Extracting text
                page_text = page.extract_text()
                if page_text:
                    all_text.append(page_text)

                # Converting page to image
                page_image = page.to_image(resolution=300)  # Higher DPI for better quality
                original = page_image.original
                if original.mode != 'RGB':
                    original = original.convert('RGB')

                # # Applying antialiasing if necessary
                # original = original.resize(original.size, Image.ANTIALIAS)

                image_path = os.path.join(images_folder_path, f"{uuid.uuid4()}.jpg")
                original.save(image_path, 'JPEG', quality=95)

        full_text = "\n".join(all_text)
        return {"pdf_text": full_text, "images_path": images_folder_path}
    except Exception as e:
        return {"error": str(e)}


def get_column_value(row, column_name):
    if column_name in row:
        return row[column_name]
    else:
        print(f"Column {column_name} not found in the data.")
        return None  # Or appropriate fallback value

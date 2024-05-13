import os
import pandas as pd
import pdfplumber
import os
import wget
from decouple import config

from custom_chains import load_image_chain, vision_model, product_info_parser
from utils import download_pdf_and_convert_to_images, get_column_value
from models import product_output_structure

# Set verbose
# globals.set_debug(True)

os.environ["OPENAI_API_KEY"] = config("OPENAI_KEY")


def prepare_prompt(product_name, row_data, pdf_text):
    prompt = f"""
    You are intelligent agent who is expert in extracting structured data from raw text.
    You specilize in extracting title/product name, product specifications and product features list from a text data of spec-sheet pdf and images of pdf pages.

    Here is data of product extracted from excel sheet = {row_data}
    Here is text extracted from spec-sheet of product called {product_name} = {pdf_text}
    

    You need to analyze it hard and extract title/product name, specifications list and  list of features into json of specified format.

    Remeber that the data is very unstructured, text is very ambigious, so you need to analyze hard 
    and extract title, specifications & features. This data will be presented on E-Commerce website.
    Images of pages of pdf file are also provided, analyze those images and use them as well.
    The features should be an html bullet list. and you must not miss any feature but also do not put anything that is not feature.
    Also do not mix specifications and features.
    The specifications should be a 2 column html table of specifications without styles or headings.
    The warranty should be in the following format: 1:Labor, 2:Parts if it says 1 year labor and 2 year parts else if it says 1 year labor and parts then you should put 1:Labor, 1:Parts. I hope you understand the format of warranty.
    Specifications extracted, must really be specifications, and features must really be features of product.
    Do not put random text into features list.
    The comma seperated certifications should be gramatically correct, e.g capitalization.
    Also I must mention that although the povided text from pdf can be different 
    but I have noticed that points starting with • or * is a feature... • or * is present before feature but sometimes * is also there for spec so think carefully.
    Also remeber to not use characters other than English.
    """
    return prompt


def get_product_informations(
    product_name, row_data, pdf_text, images_path: str
) -> dict:
    prompt = prepare_prompt(product_name, row_data, pdf_text)
    # vision_chain = load_image_chain | vision_model | product_info_parser
    vision_chain = vision_model | product_info_parser
    return vision_chain.invoke({"images_path": f"{images_path}", "prompt": prompt})


def process_excel_sheet(excel_path,row_index=None):
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()
    print(df.columns)
    print("==============")
    print(df.head())
    results_df = product_output_structure
    for index, row in df.iterrows():
        try:
            print("=======================")
            print(row)
            print("=======================")
            if row_index is not None and index!=row_index:
                continue
            pdf_file_url = row["Spec sheet"]
            if not pd.notna(pdf_file_url):
                continue

            pdf_info = download_pdf_and_convert_to_images(pdf_file_url)
            product_info = get_product_informations(
                get_column_value(row, "PRODUCT"),
                row.to_json(),
                pdf_info["pdf_text"],
                pdf_info["images_path"],
            )
            print(product_info)
            sku = get_column_value(row, "SKU")
            sku = "" if sku is None else sku
            product_name = (
                f"{get_column_value(row, 'Brand')} {sku} {get_column_value(row,'PRODUCT')}"
            )
            results_df.loc[index] = [
                product_name,
                pdf_info["pdf_text"],
                product_info["product_features"],
                product_info["product_specifications"],
                product_info["product_certifications"],
                product_info["product_warranty"],
            ]
        except Exception as ex:
            print(ex)
    results_df.to_csv("Resources/output.csv", index=False)


if __name__ == "__main__":
    excel_path = "Resources/MVP Group MAP-MCOP  MAY 1, 2024-Revised.xlsx"
    process_excel_sheet(excel_path)

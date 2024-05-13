import os
import json

from decouple import config

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

os.environ["OPENAI_API_KEY"] = config("OPENAI_KEY")


def extract_title_specs_features(product_name, pdf_text,row_data):
    prompt = f"""
    You are intelligent agent who is expert in extracting structured data from raw text.
    You specilize in extracting title/product name, product specifications and product features list from a text data of spec-sheet pdf.

    Here is data of product extracted from excel sheet = {row_data}
    Here is text extracted from spec-sheet of product called {product_name} = {pdf_text}
    

    You need to analyze it hard and extract title/product name, specifications list and  list of features into json of following format.
    {{"product_name":"product name","product_description":"description of product","product_features":"html bullet list","product_specifications":"2 columns , headless html table without styles","product_certifications":"comma seperated certifications for product, you can find certifications from extracted pdf data","product_warranty":"warranty of product in specified format"}}

    Remember that you must reply in json string.

    Remeber that the data is very unstructured, text is very ambigious, so you need to analyze hard 
    and extract title, specifications & features. This data will be presented on E-Commerce website.
    The product name should start with brand , main feature & product type. Product name should less than 120 characters.
    The description should be an ecommerce description similar to the ones found on webstaurantstore.com.
    The features should be an html bullet list.
    The specifications should be a 2 column html table of specifications without styles or headings.
    The warranty should be in the following format: 1:Labor, 2:Parts.
    Specifications extracted, must really be specifications, and features must really be features of product.
    Do not put random text into features list.
    Also I must mention that although the povided text from pdf can be different 
    but I have noticed that points starting with • is a feature... • is present before feature.
    Remeber to not use word json before JSON array of strings.
    Remeber, you do not speak other than JSON, so only return JSON array of string otherwise system will thorow error.
    """
    tries_count = 0
    while True:
        if tries_count == 3:
            return ["Unable to Find Specifications"]
        tries_count += 1
        try:
            # model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
            model = ChatOpenAI(temperature=0, model="gpt-4")
            parser = StrOutputParser()
            chain = model | parser
            response_string = chain.invoke(prompt)
            response = json.loads(response_string)
            print(response)
            return response
        except Exception as ex:
            print(ex)


def extract_specifications(product_name, pdf_text):
    prompt = f"""
    You are intelligent agent who is expert in extract structured data from raw text.
    You specilize in extract specifications list from a text data of spec-sheet pdf.

    Here is text extracted from spec-sheet of product called {product_name} = {pdf_text}

    You need to analyze it hard and extract list of specifications into json array of strings.
    You do not include features of product into specifications list.
    Example of output is ["specification 1","specification 2","and so on"]
    Remember that you must reply in json array of strings, each string is specification not a feature.
    Remeber to not use word json before JSON array of strings.
    Remeber, you do not speak other than JSON, so only return JSON array of string otherwise system will thorow error.
    """
    tries_count = 0
    while True:
        if tries_count == 3:
            return ["Unable to Find Specifications"]
        tries_count += 1
        try:
            model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106")
            parser = StrOutputParser()
            chain = model | parser
            response_string = chain.invoke(prompt)
            response = json.loads(response_string)
            print(response)
            return response
        except Exception as ex:
            print(ex)

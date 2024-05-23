from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd


class ProductInformation(BaseModel):
    """Information about an image."""
    product_description:str = Field(description="description of product in p tag")
    product_features: str = Field(description="html bullet list")
    product_specifications: str = Field(
        description="2 columns , headless html table without styles"
    )
    product_certifications: str = Field(
        description="comma seperated certifications for product, you can find certifications from extracted pdf data"
    )
    product_warranty: str = Field(description="warranty of product in specified format")


product_output_structure = pd.DataFrame(
    columns=[
        "S2.Product Name",
        "S2.Description",
        "S2.PDF Text",
        "S2.Features",
        "S2.Specifications",
        "S2.Certifications",
        "S2.Warranty",
        "S2.Error"
    ]
)

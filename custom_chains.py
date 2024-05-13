from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import TransformChain
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain

from utils import load_images
from models import ProductInformation

load_image_chain = TransformChain(
    input_variables=["images_path"],
    output_variables=["encoded_images"],
    transform=load_images,
)

product_info_parser = JsonOutputParser(pydantic_object=ProductInformation)


@chain
def vision_model(inputs: dict) -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(temperature=0.5, model="gpt-4o")
    content = [
        {"type": "text", "text": inputs["prompt"]},
        {
            "type": "text",
            "text": product_info_parser.get_format_instructions(),
        },
    ]
    if len(inputs.get("encoded_images",[])) > 0:
        for encoded_image in inputs["encoded_images"]:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                }
            )
    msg = model.invoke([HumanMessage(content=content)])
    return msg.content

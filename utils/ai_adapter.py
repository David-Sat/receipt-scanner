
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.schema.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser


def process_image(image_path: str) -> str:
        
    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)


    multimodal_prompt = HumanMessage(
        content=[
            {"type": "text", "text": "List all the items on this receipt."},
            {"type": "image_url", "image_url": image_path}
        ]
    )

    image_prompt_template = ChatPromptTemplate.from_messages([multimodal_prompt])

    chain = (
        image_prompt_template
        | vision_model
        | StrOutputParser()
    )

    output = chain.invoke({})
    return output
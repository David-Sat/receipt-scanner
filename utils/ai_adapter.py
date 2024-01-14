
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.schema.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.schema import StrOutputParser

from utils.config_loader import load_few_shot_examples
import json

example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"), 
            ("ai", "{output}"),
        ]
    )

def process_image(image_path: str) -> str:
    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)


    multimodal_prompt = HumanMessage(
        content=[
            {"type": "text", "text": "List all the items on this receipt, including their prices in a comma separated list."},
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


def create_raw_json(raw_text: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    few_shot_examples = load_few_shot_examples('configs/few_shot_examples.json')

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=few_shot_examples,
    )

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Convert the provided lists to JSON."),
                few_shot_prompt,
                ("human", raw_text)
            ] 
        )
    
    chain = (
        prompt
        | text_model
        | StrOutputParser()
    )

    output = chain.invoke({})
    return output



def enrich_json(data_raw_json: str) -> str:
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

    data = json.loads(data_raw_json)

    result = text_model.invoke("Enrich each item in the JSON with a nutritional value from 0 to 10. \n" + data_raw_json)

    return result.content


    data_dict = json.loads(data_raw_json)
    receipt_items = data_dict["receiptItems"]
    items_json = json.dumps(receipt_items)


    few_shot_examples = load_few_shot_examples('configs/few_shot_examples2.json')

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=few_shot_examples,
    )

    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Enrich the items in the JSON with a nutritional value from 0 to 10."),
                few_shot_prompt,
                ("human", items_json)
            ] 
        )
    
    chain = (
        prompt
        | text_model
        | StrOutputParser()
    )

    output = chain.invoke({})
    return output
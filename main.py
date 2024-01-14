import streamlit as st
import json
import assets

import json
from PIL import Image
from pathlib import Path
import io
import pandas as pd


from langchain_google_genai import ChatGoogleGenerativeAI
from utils.ai_adapter import process_image, create_raw_json, enrich_json, retry_function, filter_list


def get_api_key():
    if "GOOGLE_API_KEY" not in st.session_state:
        if "GOOGLE_API_KEY" in st.secrets:
            st.session_state["GOOGLE_API_KEY"] = st.secrets.google_api_key
        else:
            st.session_state["GOOGLE_API_KEY"] = st.sidebar.text_input("Google API Key", type="password")
    if not st.session_state["GOOGLE_API_KEY"]:
        st.info("Enter a Google API Key to continue")
        st.stop()   


def json_to_df(json_str):
    data = json.loads(json_str)
    return pd.DataFrame(data["receiptItems"])


def calculate_average_nutritional_level():
    file_path = "assets/example.json"
    with open(file_path, 'r') as file:
        data = json.load(file)  
    nutritional_values = [item['nutritionalValue'] for item in data['receiptItems']]
    average_nutritional_value = sum(nutritional_values) / len(nutritional_values)
    st.title("Average Nutritional Value Calculator")
    st.write("Nutritional Values:", nutritional_values)
    st.write("Average Nutritional Value:", average_nutritional_value)

def process_receipt(image_url: str) -> str:
    with st.spinner('Analysing receipt...'):
        raw_text = process_image(image_url)
        st.write(raw_text)

    with st.spinner('Filtering bought items...'):
        filtered_text = filter_list(raw_text)
        st.write(filtered_text)

    try:
        with st.spinner('Processing bought items...'):
            raw_json = retry_function(create_raw_json, filtered_text)
            st.write(raw_json)

        with st.spinner('Analysing nutritional values...'):
            enriched_json = retry_function(enrich_json, raw_json)
            st.write(enriched_json)

        st.success('Processing complete!')
        return enriched_json

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return ""



def main():
    get_api_key()
    st.title("Grocery Receipt Scanner Prototype")

    # Quick access example URLs
    example_urls = [
        "https://i.imgur.com/Eaz0cdG.jpeg",
        "https://i.imgur.com/t2o25bv.jpeg",
        "https://images.t-online.de/2021/06/89589144v1/0x0:768x1024/fit-in/__WIDTH__x0/image.jpg",
        "https://johannesjarens.files.wordpress.com/2015/12/kassenzettel-003-zettel.jpg",
    ]

    if 'image_url' not in st.session_state:
        st.session_state['image_url'] = ""

    image_url = st.text_input("Enter image URL", value=st.session_state['image_url'])


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Use Example 1"):
            st.session_state['image_url'] = example_urls[0]

    with col2:
        if st.button("Use Example 2"):
            st.session_state['image_url'] = example_urls[1]

    with col3:
        if st.button("Use Example 3"):
            st.session_state['image_url'] = example_urls[2]

    with col4:
        if st.button("Use Example 4"):
            st.session_state['image_url'] = example_urls[3]

    if st.session_state['image_url']:
        st.image(st.session_state['image_url'], caption="Image Preview", use_column_width=True)

    # Process button
    if st.button("Add Receipt", type="primary"):
        if image_url:
            output = process_receipt(image_url)

        else:
            st.error("Please enter an image URL to process.")


    if st.button("Load and Display JSON Data"):
        with open("data.json", "r") as file:
            json_data = file.read()
            df = json_to_df(json_data)
            st.write(df)



    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", stream=True, convert_system_message_to_human=True)


if __name__ == "__main__":
    main()

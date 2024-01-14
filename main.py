import streamlit as st

import json
from PIL import Image
from pathlib import Path
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from utils.ai_adapter import process_image, create_raw_json, enrich_json, retry_function


def get_api_key():
    if "GOOGLE_API_KEY" not in st.session_state:
        if "GOOGLE_API_KEY" in st.secrets:
            st.session_state["GOOGLE_API_KEY"] = st.secrets.google_api_key
        else:
            st.session_state["GOOGLE_API_KEY"] = st.sidebar.text_input("Google API Key", type="password")
    if not st.session_state["GOOGLE_API_KEY"]:
        st.info("Enter a Google API Key to continue")
        st.stop()


def process_receipt(image_url: str) -> str:
    with st.spinner('Analysing receipt...'):
        raw_text = process_image(image_url)
        st.write(raw_text)

    try:
        with st.spinner('Processing bought items...'):
            raw_json = retry_function(create_raw_json, raw_text)
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
        "https://images.t-online.de/2021/06/89589144v1/0x0:768x1024/fit-in/__WIDTH__x0/image.jpg",
        "https://johannesjarens.files.wordpress.com/2015/12/kassenzettel-003-zettel.jpg",
        "https://example.com/receipt3.jpg"
    ]

    if 'image_url' not in st.session_state:
        st.session_state['image_url'] = ""

    image_url = st.text_input("Enter image URL", value=st.session_state['image_url'])


    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Use Example 1"):
            st.session_state['image_url'] = example_urls[0]

    with col2:
        if st.button("Use Example 2"):
            st.session_state['image_url'] = example_urls[1]

    with col3:
        if st.button("Use Example 3"):
            st.session_state['image_url'] = example_urls[2]

    if st.session_state['image_url']:
        st.image(st.session_state['image_url'], caption="Image Preview", use_column_width=True)

    # Process button
    if st.button("Process Image", type="primary"):
        if image_url:
            output = process_receipt(image_url)

        else:
            st.error("Please enter an image URL to process.")





    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", stream=True, convert_system_message_to_human=True)



if __name__ == "__main__":
    main()

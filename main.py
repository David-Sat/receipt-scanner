import streamlit as st

import json
from PIL import Image
from pathlib import Path
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from utils.ai_adapter import process_image, create_raw_json, enrich_json


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
    raw_text = process_image(image_url)
    st.write(raw_text)
    raw_json = create_raw_json(raw_text)
    st.write(raw_json)
    enriched_json = enrich_json(raw_json)
    st.write(enriched_json)
    return enriched_json

def main():


    get_api_key()
    st.title("Grocery Receipt Scanner Prototype")

    # Allow the user to upload one or more images
    uploaded_files = st.file_uploader("Upload images", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

    # Display each uploaded image
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption=uploaded_file.name)

    # Process button
    if st.button("Process Images"):
        if uploaded_files:
            #image_path = "https://images.t-online.de/2021/06/89589144v1/0x0:768x1024/fit-in/__WIDTH__x0/image.jpg"
            image_path = "https://johannesjarens.files.wordpress.com/2015/12/kassenzettel-003-zettel.jpg"

            output = process_receipt(image_path)
            st.write(output)
            st.success(f"Processed {len(uploaded_files)} images.")

        else:
            st.error("Please upload at least one image to process.")




    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", stream=True, convert_system_message_to_human=True)



if __name__ == "__main__":
    main()

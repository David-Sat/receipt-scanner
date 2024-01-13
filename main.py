import streamlit as st

from PIL import Image
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from utils.ai_adapter import process_image


def get_api_key():
    if "GOOGLE_API_KEY" not in st.session_state:
        if "GOOGLE_API_KEY" in st.secrets:
            st.session_state["GOOGLE_API_KEY"] = st.secrets.google_api_key
        else:
            st.session_state["GOOGLE_API_KEY"] = st.sidebar.text_input("Google API Key", type="password")
    if not st.session_state["GOOGLE_API_KEY"]:
        st.info("Enter a Google API Key to continue")
        st.stop()

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
            image_path = "https://images.t-online.de/2021/06/89589144v1/0x0:768x1024/fit-in/__WIDTH__x0/image.jpg"
            output = process_image(image_path)
            st.write(output)
            st.success(f"Processed {len(uploaded_files)} images.")

        else:
            st.error("Please upload at least one image to process.")




    vision_model = ChatGoogleGenerativeAI(model="gemini-pro-vision", stream=True, convert_system_message_to_human=True)
    text_model = ChatGoogleGenerativeAI(model="gemini-pro", stream=True, convert_system_message_to_human=True)



if __name__ == "__main__":
    main()

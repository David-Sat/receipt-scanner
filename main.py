import streamlit as st
import json
import assets

import json
from PIL import Image
from pathlib import Path
import io
import pandas as pd


from utils.ai_adapter import process_image, create_raw_json, enrich_json, retry_function, filter_list, get_healthy_alternatives


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
    if 'receipt_data' in st.session_state and st.session_state['receipt_data'].get('receiptItems'):
        nutritional_values = [item['nutritionalValue'] for item in st.session_state['receipt_data']['receiptItems']]
        
        if nutritional_values:
            average_nutritional_value = sum(nutritional_values) / len(nutritional_values)
            st.title("Nutritional Insights")
            st.write("Average Nutritional Value:", average_nutritional_value)
            chart_data = {'Nutritional Values': nutritional_values, 'Average': [average_nutritional_value] * len(nutritional_values)}
            st.line_chart(chart_data)
        else:
            st.write("No nutritional data available to calculate average.")
    else:
        st.write("No data available in the session state.")


def get_three_least_nutritious_items():
    file_path = "data.json"
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        items = data['receiptItems']
        sorted_items = sorted(items, key=lambda x: x['nutritionalValue'])
        least_nutritious_items = sorted_items[:3]
        
        return least_nutritious_items

    except Exception as e:
        st.error(f"An error occurred while loading or processing the data: {e}")
        return []

def get_and_display_healthy_alternatives(unhealthy_items_str):
    try:
        with st.spinner('Finding healthy alternatives...'):
            healthy_alternatives = get_healthy_alternatives(unhealthy_items_str)
            st.success('Healthy alternatives found!')
            st.write(healthy_alternatives)
            st.write("Healthier alternatives are always provided in the same price range.")
    except Exception as e:
        st.error(f"An error occurred while finding healthy alternatives: {e}")

def process_receipt(image_url: str) -> str:
    with st.spinner('Analysing receipt...'):
        raw_text = process_image(image_url)

    with st.spinner('Filtering bought items...'):
        filtered_text = filter_list(raw_text)

    try:
        with st.spinner('Processing bought items...'):
            raw_json = retry_function(create_raw_json, filtered_text)

        with st.spinner('Analysing nutritional values...'):
            enriched_json = retry_function(enrich_json, raw_json)

        new_items = json.loads(enriched_json)["receiptItems"]
        st.session_state['receipt_data']['receiptItems'].extend(new_items)

        st.success('Processing complete!')
        return enriched_json

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return ""



def main():
    get_api_key()
    st.title("nourishLens")
    st.subheader("A receipt analysis tool to fight malnutrition")
    st.write("nourishLens won at both the local Munich GDSC Ideathon and the Europe-wide competition. It revolutionizes nutritional awareness for low-income families, offering intuitive, cost-effective food choices without the hassle of manual entry. By analyzing grocery receipts, nourishLens simplifies healthy living, bridging the gap in health inequality.")

    if 'receipt_data' not in st.session_state:
        try:
            with open("data.json", "r") as file:
                st.session_state['receipt_data'] = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            st.session_state['receipt_data'] = {"receiptItems": []}

    # Quick access example URLs
    example_urls = [
        "https://i.imgur.com/Eaz0cdG.jpeg",
        "https://i.imgur.com/t2o25bv.jpeg",
        "https://images.t-online.de/2021/06/89589144v1/0x0:768x1024/fit-in/__WIDTH__x0/image.jpg",
        "https://johannesjarens.files.wordpress.com/2015/12/kassenzettel-003-zettel.jpg",
    ]

    if 'image_url' not in st.session_state:
        st.session_state['image_url'] = ""

    image_url = st.text_input("Enter image URL of a receipt or select one of the examples below.", value=st.session_state['image_url'])


    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Example 1"):
            st.session_state['image_url'] = example_urls[0]

    with col2:
        if st.button("Example 2"):
            st.session_state['image_url'] = example_urls[1]

    with col3:
        if st.button("Example 3"):
            st.session_state['image_url'] = example_urls[2]


    if st.session_state['image_url']:
        st.image(st.session_state['image_url'], caption="Image Preview", use_column_width=True)

    # Process button
    if st.button("Add Receipt", type="primary"):
        if image_url:
            output = process_receipt(image_url)

        else:
            st.error("Please enter an image URL to process.")


    if st.button("Load and Display Groceries of the Last Month"):
        if 'receipt_data' in st.session_state and st.session_state['receipt_data']:
            # Convert the session state data to JSON string
            json_data = json.dumps(st.session_state['receipt_data'])
            df = json_to_df(json_data)
            st.write(df)
        else:
            st.write("No data available in the session state.")


    if st.button("Display Healthier Alternatives"):
        least_nutritious_items = get_three_least_nutritious_items()
        
        unhealthy_items_str = ", ".join([f"{item['itemName']} ${item['price']}" for item in least_nutritious_items])

        if unhealthy_items_str:
            get_and_display_healthy_alternatives(unhealthy_items_str)
        else:
            st.write("No items to find alternatives for.")


    calculate_average_nutritional_level()


if __name__ == "__main__":
    main()

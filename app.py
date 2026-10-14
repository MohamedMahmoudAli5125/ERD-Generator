import os
from PIL import Image
import streamlit as st
from pydantic import ValidationError
from gemini_service import generate_erd_json_from_text , GEMINI_MODEL_NAME
from parser import parse_erd_json
from diagram_renderer import render_graph
from datetime import datetime

img = Image.open("logo.png")
st.set_page_config(
    page_title="ERD Generator",
    page_icon=img,    
    layout="wide"    
)

st.sidebar.header("⚙️ Export Settings")
output_format = st.sidebar.selectbox(
    "Choose Output Format:", 
    ["png", "pdf", "svg", "jpeg"]
)

OUTPUT_BASE_DIR = "output"
MANUAL_DIR = os.path.join(OUTPUT_BASE_DIR, "manual_json")
AI_DIR = os.path.join(OUTPUT_BASE_DIR, "ai_generated")

def get_unique_filename(prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"

col1, col2 = st.columns([1, 8])
with col1:
    st.image(img, width=80) 
with col2:
    st.title("ERD Generator")
    
mode = st.radio("Choose Input Mode:", ["JSON Input", "Textual Description" , "Compare Both"], horizontal=True)
st.divider()

if mode == "JSON Input":
    st.subheader("Upload or Paste JSON")
    json_content = None

    json_input = st.text_area("Paste your ERD JSON here", height=200)
    uploaded_file = st.file_uploader("Upload JSON file", type=["json"] , accept_multiple_files=False)
    if uploaded_file is not None:
        json_content = uploaded_file.read().decode("utf-8")
    if json_content:
        json_input = json_content

    if st.button("Parse JSON"):
        if json_input.strip():
            try:
                erd_schema = parse_erd_json(json_input)
                filename = get_unique_filename("manual_erd")
                dot = render_graph(erd_schema, filename=filename, directory=MANUAL_DIR, file_format=output_format)
                st.success(f"JSON Parsed & Graph saved to `{MANUAL_DIR}/{filename}.{output_format}`")
                st.graphviz_chart(dot)
                
                st.write("Parsed ERD Schema:")
                with st.expander("View JSON Data"):
                    st.json(erd_schema.model_dump())
        
            except ValidationError:
                st.error("Failed to parse the JSON. Please check the format.")
        else:
            st.warning("Please provide JSON input either by pasting or uploading a file.")

elif mode == "Textual Description":
    
    st.subheader("Describe your Database")
    st.markdown(f" **Powered by AI** *(Model: `{GEMINI_MODEL_NAME}`)*")
    
    text_input = st.text_area("Enter textual description", height=200, placeholder="e.g., I have a system with Users, Orders, and Products...")
    
    if st.button("Generate ERD from Text"):
        if text_input.strip():
            with st.spinner("Analyzing text and generating ERD..."):
                generated_json = generate_erd_json_from_text(text_input)
                
                if generated_json:
                    try:
                        erd_schema = parse_erd_json(generated_json)
                        filename = get_unique_filename("ai_erd")
                        dot = render_graph(erd_schema, filename=filename, directory=AI_DIR, file_format=output_format)
                        st.success(f" AI Generated ERD saved to `{AI_DIR}/{filename}.{output_format}`")
                        
                        st.graphviz_chart(dot)
                        
                        with st.expander("View Generated JSON Data"):
                            st.json(erd_schema.model_dump())
                    except ValidationError:
                        st.error("Failed to parse the AI-generated JSON.")
                else:
                    st.error("AI Service failed to generate a valid response.")
        else:
            st.warning("Please enter a description first.")
            
elif mode == "Compare Both":
    st.subheader("Compare JSON Output vs AI Text Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("1. Manual JSON Input")
        json_content = None
        json_input_compare = st.text_area("Paste ERD JSON", height=200, key="json_comp")
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"] , accept_multiple_files=False , key="file_comp")
        if uploaded_file is not None:
            json_content = uploaded_file.read().decode("utf-8")
        if json_content:
            json_input_compare = json_content
        
    with col2:
        st.markdown(f"**2. Textual Description**  *(AI: `{GEMINI_MODEL_NAME}`)*")
        text_input_compare = st.text_area("Enter text description", height=200, key="text_comp")
        
    if st.button("Generate and Compare"):
        if json_input_compare.strip() and text_input_compare.strip():
            
            with st.spinner("Analyzing text and generating AI ERD..."):
                generated_json_compare = generate_erd_json_from_text(text_input_compare)
            
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                st.markdown("### Manual JSON ERD")
                try:
                    erd_schema_manual = parse_erd_json(json_input_compare)
                    filename_manual = get_unique_filename("compare_manual")
                    dot_manual = render_graph(erd_schema_manual , filename=filename_manual, directory=MANUAL_DIR, file_format=output_format)
                    st.success(f"Saved: `{filename_manual}.{output_format}`")
                    st.graphviz_chart(dot_manual)
                except ValidationError:
                    st.error("Failed to parse the manual JSON.")
                    
            with res_col2:
                st.markdown("### AI Generated ERD")
                if generated_json_compare:
                    try:
                        erd_schema_ai = parse_erd_json(generated_json_compare)
                        filename_ai = get_unique_filename("compare_ai")
                        dot_ai = render_graph(erd_schema_ai , filename=filename_ai, directory=AI_DIR, file_format=output_format)
                        st.success(f"Saved: `{filename_ai}.{output_format}`")
                        st.graphviz_chart(dot_ai)
                    except ValidationError:
                        st.error("Failed to parse the AI-generated JSON.")
                else:
                    st.error("AI Service failed to generate a valid response.")
        else:
            st.warning("Please provide both JSON and Textual description.")
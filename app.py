import os
import base64
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

layout_choice = st.sidebar.selectbox(
    "Choose Diagram Layout:",
    ["Hierarchical (LR)", "Star (Radial)"]
)

OUTPUT_BASE_DIR = "output"
MANUAL_DIR = os.path.join(OUTPUT_BASE_DIR, "manual_json")
AI_DIR = os.path.join(OUTPUT_BASE_DIR, "ai_generated")

def get_unique_filename(prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}"

DISPLAYABLE_FORMATS = ["png", "jpeg", "svg"]

def export_erd(erd_schema, filename, directory):
    render_graph(erd_schema, filename=filename, directory=directory, file_format=output_format, layout=layout_choice)
    saved_path = os.path.join(directory, f"{filename}.gv.{output_format}")
    preview_path = saved_path
    if output_format not in DISPLAYABLE_FORMATS:
        render_graph(erd_schema, filename=filename, directory=directory, file_format="png", layout=layout_choice)
        preview_path = os.path.join(directory, f"{filename}.gv.png")
        st.info(f"`{output_format}` can't be previewed, so a PNG copy was also saved for preview.")
    return saved_path, preview_path

def show_preview(preview_path):
    if preview_path.endswith(".svg"):
        with open(preview_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" style="max-width:100%">', unsafe_allow_html=True)
    else:
        st.image(preview_path)

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
                saved_path, preview_path = export_erd(erd_schema, filename, MANUAL_DIR)
                st.success(f"JSON Parsed & Graph saved to `{saved_path}`")
                show_preview(preview_path)
                
                st.write("Parsed ERD Schema:")
                with st.expander("View JSON Data"):
                    st.json(erd_schema.model_dump())
        
            except ValidationError:
                st.error("Failed to parse the JSON. Please check the format.")
            except Exception as e:
                st.error(f"Something went wrong while generating the diagram: {e}")
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
                        saved_path, preview_path = export_erd(erd_schema, filename, AI_DIR)
                        st.success(f" AI Generated ERD saved to `{saved_path}`")
                        
                        show_preview(preview_path)
                        
                        with st.expander("View Generated JSON Data"):
                            st.json(erd_schema.model_dump())
                    except ValidationError:
                        st.error("Failed to parse the AI-generated JSON.")
                    except Exception as e:
                        st.error(f"Something went wrong while generating the diagram: {e}")
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
                    saved_manual, preview_manual = export_erd(erd_schema_manual, filename_manual, MANUAL_DIR)
                    st.success(f"Saved: `{saved_manual}`")
                    show_preview(preview_manual)
                except ValidationError:
                    st.error("Failed to parse the manual JSON.")
                except Exception as e:
                    st.error(f"Something went wrong while generating the diagram: {e}")
                    
            with res_col2:
                st.markdown("### AI Generated ERD")
                if generated_json_compare:
                    try:
                        erd_schema_ai = parse_erd_json(generated_json_compare)
                        filename_ai = get_unique_filename("compare_ai")
                        saved_ai, preview_ai = export_erd(erd_schema_ai, filename_ai, AI_DIR)
                        st.success(f"Saved: `{saved_ai}`")
                        show_preview(preview_ai)
                    except ValidationError:
                        st.error("Failed to parse the AI-generated JSON.")
                    except Exception as e:
                        st.error(f"Something went wrong while generating the diagram: {e}")
                else:
                    st.error("AI Service failed to generate a valid response.")
        else:
            st.warning("Please provide both JSON and Textual description.")
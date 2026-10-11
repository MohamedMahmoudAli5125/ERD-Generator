import streamlit as st
from pydantic import ValidationError
from parser import parse_erd_json

st.title("ERD JSON Parser")
json_content = None

json_input = st.text_area("Paste your ERD JSON here", height=250)

uploaded_file = st.file_uploader("Upload JSON file", type=["json"] , accept_multiple_files=False)
if uploaded_file is not None:
    json_content = uploaded_file.read().decode("utf-8")
if json_content:
    json_input = json_content

if st.button("Parse JSON"):
    try:
        erd_schema = parse_erd_json(json_input)
        st.write("Parsed ERD Schema:")
        st.json(erd_schema.model_dump())
        # erd_schema_json = erd_schema.entities
        # print(erd_schema.entities)
        # for entity in erd_schema.entities:
        #     isWeak = 1
        #     for attribute in entity.attributes:
        #         if attribute.isPrimaryKey:
        #             isWeak = 0;
        #             break
        #     if isWeak:
                
                
        #         st.warning(f"\nEntity '{entity.name}' is a weak entity (no primary key found).\n")
        #         entity.weak = True
        # print(erd_schema.entities)    
    except ValidationError:
        st.error("Failed to parse the JSON.")

st.write("Uploaded JSON content:")
st.code(json_input, language="json")

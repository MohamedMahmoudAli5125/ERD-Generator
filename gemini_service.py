from parser import parse_erd_json
from diagram_renderer import render_graph
import os
from time import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schemas import ERDiagramSchema
from pydantic import ValidationError

    
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
client = genai.Client(api_key=API_KEY)

def generate_erd_json_from_text(system_description):  
    prompt = f"""
        You are an expert database designer and data modeler.
        Analyze the following system description and extract the Entity-Relationship Diagram (ERD) components:
        - Entities (with their attributes, primary keys, and whether they are weak entities).
        - Relationships (connecting entities, cardinality, participation, and any relationship attributes).
        - In a relationship, entity1/entity2/entity3, the cardinality list, and the participation list must all follow the same order.
        - cardinality has one value per entity: "1", "N" or "M" (e.g. ["N","1"] or ["M","N","1"]).
        - participation has one value per entity: "total" if every instance must participate, otherwise "partial".
        - A weak entity always has total participation in its identifying relationship.
        - minCardinality/maxCardinality are per entity, in the same order as entity1/2/3.
        Fill an entity's slot ONLY if the description gives explicit numeric bounds for that specific entity (e.g. "between 5 and 50 employees").
        For every other entity use "" in both lists.
        If no entity in the relationship has explicit bounds, leave both lists null.

        System Description:
        "{system_description}"
        """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite', # tried models 3.5 , 3.6 and 3.8 flash and all give me alot of 503 errors(high demand ), so I settled on 3.5 flash-lite which is the most stable one
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ERDiagramSchema  
            ),
        )
        
        json_result = response.text
        try:
            ERDiagramSchema.model_validate_json(json_result)
        except ValidationError as e:
            print("Gemini API returned an invalid JSON matching the schema:")
            print(e)
            return None

        return json_result
        
    except Exception as e:
        print(f"An error occurred while communicating with Gemini API: {e}")
        return None

if __name__ == "__main__":
    sample_description = """
        We need to design a database system for a company.
        An Employee has a unique SSN, a composite Name (consisting of a FirstName and LastName), one or more Phone numbers, and a derived Age.
        A Department has a unique DeptID and a DeptName.
        A Dependent is a weak entity, identified by a partial key Dep_Name, and also has a Relation to the employee.
        A Project has a unique ProjectID and a Location.

        Relationships:
        - Works_In: every employee works in exactly one department. Every department must have between 5 and 50 employees.
        - Has_Dependents: an employee can have many dependents, or none. Every dependent must belong to an employee. This is the identifying relationship of the weak entity Dependent.
        - Assigned_To: a ternary relationship between Employee, Project and Department. An employee can work on many projects, and a project can have many employees. For a given employee and project, there is exactly one department. All participations are partial. We track the 'Hours' worked for each assignment.
        """
    print("Sending request to Gemini...")  
    t0 = time()
    generated_json = generate_erd_json_from_text(sample_description)
    print(f"Time taken: {time() - t0:.2f} seconds")
    if generated_json:
        print("\nSuccessfully generated JSON:\n", generated_json)
        
        print("\nParsing and rendering the ERD graph...")
        erd_schema = parse_erd_json(generated_json)
        render_graph(erd_schema, filename='ai_generated_erd', directory='doctest-output')
        print("Done!")
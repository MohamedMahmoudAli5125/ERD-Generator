import os
import time
from flask.cli import load_dotenv
from google import genai
from google.genai import types
from schemas import ERDiagramSchema
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.5-flash-lite"

tests = {
    "1_بدون config": None,
    "2_json بس": types.GenerateContentConfig(response_mime_type="application/json"),
    "3_json + schema": types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ERDiagramSchema,
    ),
    "4_json + schema + thinking": types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ERDiagramSchema,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
}

for name, cfg in tests.items():
    t0 = time.time()
    try:
        client.models.generate_content(
            model=MODEL,
            contents="An Employee has an SSN and a Name. A Department has a DeptID. Employee works in Department (N:1).",
            config=cfg,
        )
        print(f"OK   {name}  {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"FAIL {name}  {str(e)[:150]}")
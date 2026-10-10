from schemas import ERDiagramSchema
from pydantic import ValidationError

def parse_erd_json(json_str: str) -> ERDiagramSchema:
    try:
        diagram_data = ERDiagramSchema.model_validate_json(json_str)
        return diagram_data
    except ValidationError as e:
        print("Invalid ERD JSON format:", e)
        raise e
if __name__ == "__main__":
    example_json = '''
    {
        "entities": [
            {
                "name": "Student",
                "attributes": [
                    {"name": "student_id", "isPrimaryKey": true},
                    {"name": "name"},
                    {"name": "email"}
                ]
            },
            {
                "name": "Course",
                "attributes": [
                    {"name": "course_id", "isPrimaryKey": true},
                    {"name": "title"},
                    {"name": "credits"}
                ]
            }
        ],
        "relationships": [
            {
                "name": "Enrollment",
                "entity1": "Student",
                "entity2": "Course",
                "cardinality": "M:N"
            }
        ]
    }
    '''
    try:
        erd_schema = parse_erd_json(example_json)
        print("Parsed ERD Schema:", erd_schema)
    except ValidationError:
        print("Failed to parse the example JSON.")
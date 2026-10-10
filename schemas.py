from typing import List, Optional
from pydantic import BaseModel, Field

class Attribute(BaseModel):
    name: str
    isPrimaryKey: bool = False
    isMultiValued: bool = False
    composite: Optional[List[str]] = None

class Entity(BaseModel):
    name: str
    attributes: List[Attribute] = Field(default_factory=list)

class Relationship(BaseModel):
    name: str
    entity1: str
    entity2: str
    entity3: str = None  
    cardinality: str 
class ERDiagramSchema(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
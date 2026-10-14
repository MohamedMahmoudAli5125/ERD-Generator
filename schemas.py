from typing import List, Optional
from pydantic import BaseModel, Field

class Attribute(BaseModel):
    name: str
    isPrimaryKey: bool = False
    isMultiValued: bool = False
    composite: Optional[List[Attribute]] = None
    isPartialKey: bool = False
    isDerived: bool = False
    
class Entity(BaseModel):
    name: str
    attributes: List[Attribute] = Field(default_factory=list)
    weak: bool = False
class Relationship(BaseModel):
    name: str
    entities: List[Entity] = Field(default_factory=list)  
    cardinality: List[str] = Field(default_factory=list) 
    participation: List[str] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    identifyingRelationship: bool = False
    minCardinality: Optional[List[str]] = None # List of minimum cardinalities for each entity in the relationship
    maxCardinality: Optional[List[str]] = None # List of maximum cardinalities for each entity in the relationship
    
class ERDiagramSchema(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
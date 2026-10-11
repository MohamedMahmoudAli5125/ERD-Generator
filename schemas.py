from typing import List, Optional
from pydantic import BaseModel, Field

class Attribute(BaseModel):
    name: str
    isPrimaryKey: bool = False
    isMultiValued: bool = False
    composite: Optional[List[str]] = None
    isPartialKey: bool = False
    isDerived: bool = False
    
class Entity(BaseModel):
    name: str
    attributes: List[Attribute] = Field(default_factory=list)
    weak: bool = False
class Relationship(BaseModel):
    name: str
    entity1: str
    entity2: str
    entity3: Optional[str] = None  
    cardinality: str #1:N:M
    participation: List[str] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    identifyingRelationship: bool = False
    minCardinality: Optional[str] = None
    maxCardinality: Optional[str] = None
    
class ERDiagramSchema(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
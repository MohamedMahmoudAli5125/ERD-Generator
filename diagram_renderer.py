import os

import graphviz
from parser import parse_erd_json

def render_graph(graph, filename='graph', directory='output', file_format='png'):
    os.makedirs(directory, exist_ok=True)
    dot = graphviz.Digraph(filename, comment='Graph', format=file_format)
    dot.attr(rankdir='LR' , splines='polyline', ranksep='1.8', nodesep='0.4')    
    dot.attr('node', fontname='Times New Roman,', fontsize='12')
    dot.attr('edge', fontname='Times New Roman,', fontsize='11')
    
    for entity in graph.entities:
        handle_entity(dot, entity)
            
    for relationship in graph.relationships:
        handle_relationship(dot, relationship)
            
    dot.render(directory=directory, view=False, cleanup=True)    
    return dot
    
def card_label(rel, i, default):
    mins = rel.minCardinality or []
    maxs = rel.maxCardinality or []
    mn = mins[i] if i < len(mins) else ""
    mx = maxs[i] if i < len(maxs) else ""
    return f"{mn}..{mx}" if mn and mx else default
  
def handle_composite_attributes(dot, parent_node_id, composite_attributes):
    for sub_attr in composite_attributes:
        sub_attr_name = sub_attr.name if hasattr(sub_attr, 'name') else sub_attr
        
        sub_node_id = f"{parent_node_id}_{sub_attr_name}"
        
        dot.node(sub_node_id, sub_attr_name, shape='ellipse')
        dot.edge(parent_node_id, sub_node_id, arrowhead='none')
        
        if hasattr(sub_attr, 'composite') and sub_attr.composite:
            handle_composite_attributes(dot, sub_node_id, sub_attr.composite)

def render_attributes(dot, owner_name, attributes):
    for attribute in attributes:
        node_id = f"{owner_name}_{attribute.name}"
        
        if attribute.isPrimaryKey:
            dot.node(node_id, f"<<u>{attribute.name}</u>>", shape='ellipse')   
        elif attribute.isPartialKey:
            dotted_label = f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD BORDER="1" SIDES="B" STYLE="DOTTED">{attribute.name}</TD></TR></TABLE>>'
            dot.node(node_id, dotted_label, shape='ellipse')              
        elif attribute.isMultiValued:
            dot.node(node_id, attribute.name, shape='ellipse', peripheries='2')
        elif attribute.isDerived:
            dot.node(node_id, attribute.name, shape='ellipse', style='dashed')
        else:
            dot.node(node_id, attribute.name, shape='ellipse')
            
        dot.edge(owner_name, node_id, arrowhead='none')
        
        if attribute.composite:
            handle_composite_attributes(dot, node_id, attribute.composite)
            
def handle_entity(dot, entity):
    if entity.weak:
        dot.node(entity.name, entity.name, shape='rectangle', peripheries='2', style='filled', fillcolor='lightgrey')
    else:
        dot.node(entity.name, entity.name, shape='rectangle', style='filled', fillcolor='lightgrey')  
    render_attributes(dot, entity.name, entity.attributes)                

def handle_relationship(dot, relationship):
    if relationship.identifyingRelationship:
        dot.node(relationship.name, relationship.name, shape='diamond', peripheries='2', style='filled', fillcolor='lightgrey')  
    else:
        dot.node(relationship.name, relationship.name, shape='diamond', style='filled', fillcolor='lightgrey') 
        
    render_attributes(dot, relationship.name, relationship.attributes)
    
    cards = relationship.cardinality
    parts = relationship.participation
    
    for i, entity in enumerate(relationship.entities):
        card_val = cards[i] if i < len(cards) else ""
        c_label = card_label(relationship, i, card_val)
        
        is_total = i < len(parts) and parts[i] == "total"
        edge_style = {'color': 'black:black'} if is_total else {}
        
        dot.edge(entity.name, relationship.name, label=f' {c_label} ', arrowhead='none', fontsize='12', **edge_style)
     
   
if __name__ == "__main__":

    json = '''
  {
  "entities": [
    {
      "name": "Employee",
      "weak": false,
      "attributes": [
        { "name": "SSN", "isPrimaryKey": true },
        { "name": "Name", "composite": [
          { "name": "FirstName" },
          { "name": "LastName" }
        ] },
        { "name": "Phone", "isMultiValued": true },
        { "name": "Age", "isDerived": true }
      ]
    },
    {
      "name": "Department",
      "weak": false,
      "attributes": [
        { "name": "DeptID", "isPrimaryKey": true },
        { "name": "DeptName" }
      ]
    },
    {
      "name": "Dependent",
      "weak": true,
      "attributes": [
        { "name": "Dep_Name", "isPartialKey": true },
        { "name": "Relation" }
      ]
    },
    {
      "name": "Project",
      "weak": false,
      "attributes": [
        { "name": "ProjectID", "isPrimaryKey": true },
        { "name": "Location" }
      ]
    }
  ],
  "relationships": [
    {
      "name": "Works_In",
      "entities": [{"name": "Employee"}, {"name": "Department"}],
      "cardinality": ["N", "1"],
      "participation": ["total", "total"],
      "minCardinality": ["", "5"],
      "maxCardinality": ["", "50"]
    },
    {
      "name": "Has_Dependents",
      "entities": [{"name": "Employee"}, {"name": "Dependent"}],
      "cardinality": ["1", "N"],
      "participation": ["partial", "total"],
      "identifyingRelationship": true
    },
    {
      "name": "Assigned_To",
      "entities": [{"name": "Employee"}, {"name": "Project"}, {"name": "Department"}],
      "cardinality": ["M", "N", "1"],
      "participation": ["partial", "partial", "partial"],
      "attributes": [
        { "name": "Hours" }
      ]
    }
  ]
}
        '''
    graph = parse_erd_json(json_str=json)
    render_graph(graph, filename='erd_graph', directory='doctest-output')
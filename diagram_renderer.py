import graphviz
from parser import parse_erd_json

def render_graph(graph, filename='graph', directory='doctest-output'):
    dot = graphviz.Digraph(filename, comment='Graph', format='png')
    dot.attr(rankdir='LR' , splines='polyline', ranksep='1.8', nodesep='0.4')    
    dot.attr('node', fontname='Times New Roman,', fontsize='12')
    dot.attr('edge', fontname='Times New Roman,', fontsize='11')
    
    for entity in graph.entities:
        handle_entity(dot, entity)
            
    for relationship in graph.relationships:
        handle_relationship(dot, relationship)
            
    dot.render(directory=directory, view=True)    
    
def card_label(rel, i, default):
    mins = rel.minCardinality or []
    maxs = rel.maxCardinality or []
    mn = mins[i] if i < len(mins) else ""
    mx = maxs[i] if i < len(maxs) else ""
    return f"{mn}..{mx}" if mn and mx else default
  
def handle_attributes(dot, entity):
    for attribute in entity.attributes:
        node_id = f"{entity.name}_{attribute.name}"
        
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
            
        dot.edge(entity.name, node_id, arrowhead='none')
        
        if attribute.composite:
            for sub_attr in attribute.composite:
                sub_node_id = f"{entity.name}_{sub_attr}"
                dot.node(sub_node_id, sub_attr, shape='ellipse')
                dot.edge(node_id, sub_node_id, arrowhead='none')
                
def handle_entity(dot, entity):
    if entity.weak:
        dot.node(entity.name, entity.name, shape='rectangle', peripheries='2', style='filled', fillcolor='lightgrey')
    else:
        dot.node(entity.name, entity.name, shape='rectangle', style='filled', fillcolor='lightgrey')  
    handle_attributes(dot, entity)    
                
def handle_relationship(dot, relationship):
    if relationship.identifyingRelationship:
        dot.node(relationship.name, relationship.name, shape='diamond', peripheries='2', style='filled', fillcolor='lightgrey')  
    else:
        dot.node(relationship.name, relationship.name, shape='diamond', style='filled', fillcolor='lightgrey') 
        
    cards = relationship.cardinality
    c1 = card_label(relationship, 0, cards[0] if len(cards) > 0 else "")
    c2 = card_label(relationship, 1, cards[1] if len(cards) > 1 else "")
    c3 = card_label(relationship, 2, cards[2] if len(cards) > 2 else "")
    
    for attribute in relationship.attributes:
        attr_node_id = f"{relationship.name}_{attribute}"
        dot.node(attr_node_id, attribute, shape='ellipse')
        dot.edge(relationship.name, attr_node_id, arrowhead='none')
    
    total1 = len(relationship.participation) > 0 and relationship.participation[0] == "total" 
    edge_style1 = {'color': 'black:black'} if total1 else {}
    total2 = len(relationship.participation) > 1 and relationship.participation[1] == "total"
    edge_style2 = {'color': 'black:black'} if total2 else {}
    total3 = len(relationship.participation) > 2 and relationship.participation[2] == "total"
    edge_style3 = {'color': 'black:black'} if total3 else {}
    
    dot.edge(relationship.entity1, relationship.name, label=f' {c1} ', arrowhead='none', fontsize='12', **edge_style1)
    dot.edge(relationship.entity2, relationship.name, label=f' {c2} ', arrowhead='none', fontsize='12', **edge_style2)
    if relationship.entity3:
        dot.edge(relationship.entity3, relationship.name, label=f' {c3} ', arrowhead='none', fontsize='12', **edge_style3)

     
   
if __name__ == "__main__":

    json = '''
    {
  "entities": [
    {
      "name": "Employee",
      "weak": false,
      "attributes": [
        { "name": "SSN", "isPrimaryKey": true },
        { "name": "Name", "composite": ["FirstName", "LastName"] },
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
      "entity1": "Employee",
      "entity2": "Department",
      "cardinality": ["N", "1"],
      "participation": ["total", "total"],
      "minCardinality": ["", "5"],
      "maxCardinality": ["", "50"]
    },
    {
      "name": "Has_Dependents",
      "entity1": "Employee",
      "entity2": "Dependent",
      "cardinality": ["1", "N"],
      "participation": ["partial", "total"],
      "identifyingRelationship": true
    },
    {
      "name": "Assigned_To",
      "entity1": "Employee",
      "entity2": "Project",
      "entity3": "Department",
      "cardinality": ["M", "N", "1"],
      "participation": ["partial", "partial", "partial"],
      "attributes": ["Hours"]
    }
  ]
}
        '''
    graph = parse_erd_json(json_str=json)
    render_graph(graph, filename='erd_graph', directory='doctest-output')
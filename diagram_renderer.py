import graphviz
from parser import parse_erd_json
# dot = graphviz.Digraph('round-table', comment='The Round Table' , format='png')  
# dot.node('A', 'King Arthur')  
# dot.node('B', 'Sir Bedevere the Wise')
# dot.node('L', 'Sir Lancelot the Brave')

# dot.edges(['AB', 'AL'])
# dot.edge('B', 'L', constraint='false')
# print(dot.source)   
# dot.render(directory='doctest-output', view=True)  
# ni = graphviz.Graph('ni' ,format='png')  
# ni.attr('node', shape='rectangle')
# ni.node('A', 'Entity A')
# print(ni.source)   
# ni.render(directory='doctest-output', view=True)  
def render_graph(graph, filename='graph', directory='doctest-output'):
    dot = graphviz.Digraph(filename, comment='Graph', format='png')
    for entity in graph.entities:
        if entity.weak:
            dot.node(entity.name, entity.name,shape='rectangle', peripheries='2')
        else:
            dot.node(entity.name, entity.name, shape='rectangle')
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
                
            dot.edge(entity.name, node_id , arrowhead='none')
            
            if attribute.composite:
                for sub_attr in attribute.composite:
                    sub_node_id = f"{entity.name}_{sub_attr}"
                    dot.node(sub_node_id, sub_attr, shape='ellipse')
                    dot.edge(node_id, sub_node_id , arrowhead='none')
    for relationship in graph.relationships:
        if relationship.identifyingRelationship:
            dot.node(relationship.name, relationship.name, shape='diamond', peripheries='2')
        else:
            dot.node(relationship.name, relationship.name, shape='diamond')
            
        if relationship.cardinality:
            cards = relationship.cardinality.split(':')
        else:
            cards = []
        c1 = cards[0] if len(cards) > 0 else ""
        c2 = cards[1] if len(cards) > 1 else ""
        c3 = cards[2] if len(cards) > 2 else ""
        if relationship.minCardinality and relationship.maxCardinality:
            c1 += f" ({relationship.minCardinality}, {relationship.maxCardinality})"

        dot.edge(relationship.entity1, relationship.name, label=c1, arrowhead='none'    )
        dot.edge(relationship.entity2, relationship.name, label=c2, arrowhead='none')
        if relationship.entity3:
            dot.edge(relationship.entity3, relationship.name, label=c3, arrowhead='none')

        for attribute in relationship.attributes:
            dot.node(f"{relationship.name}_{attribute}", attribute, shape='ellipse')
            dot.edge(relationship.name, f"{relationship.name}_{attribute}" , arrowhead='none')
    dot.render(directory=directory, view=True)
   
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
      "cardinality": "N:1",
      "participation": ["total", "partial"]
    },
    {
      "name": "Has_Dependents",
      "entity1": "Employee",
      "entity2": "Dependent",
      "cardinality": "1:N",
      "identifyingRelationship": true
    },
    {
      "name": "Assigned_To",
      "entity1": "Employee",
      "entity2": "Project",
      "entity3": "Department",
      "cardinality": "M:N:1",
      "minCardinality": "1",
      "maxCardinality": "N",
      "attributes": [
        "Hours"
      ]
    }
  ]
}
        '''
    graph = parse_erd_json(json_str=json)
    render_graph(graph, filename='erd_graph', directory='doctest-output')
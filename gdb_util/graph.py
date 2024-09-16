import graphviz

class BaseColorMapper:
    def map(self, node_identifier):
        return {}

class DotGraphBuilder:
    def __init__(self, dot=None, color_mapper=None, **kwargs):
        if not dot:
            u_graph_attr = kwargs.get('graph_attr', {})
            graph_attr={'compound': 'true', **u_graph_attr}
            kwargs = {**kwargs, 'graph_attr': graph_attr}
            dot = graphviz.Digraph(**kwargs)

        self.dot = dot
        self.color_mapper = color_mapper if color_mapper else BaseColorMapper()

    def add_node(self, name, label, node_identifier=None, **kwargs):
        color_spec = self.color_mapper.map(node_identifier)
        extra_args = {**color_spec, **kwargs}
        self.dot.node(name, label, **extra_args)

    def add_edge(self, a, b, **kwargs):
        self.dot.edge(a, b, **kwargs)

    def subgraph(self, name, node_identifier=None, **kwargs):
        color_spec = self.color_mapper.map(node_identifier)
        sub = DotGraphBuilder(name=f"cluster_{name}", graph_attr={'label': f'{name}', **color_spec, 'style': 'striped'}, color_mapper=self.color_mapper)
        sub.add_node(name=name, label="", shape="point", style="invis")
        return sub
    
    def add_subgraph(self, g, node_identifier=None, **kwargs):
        color_spec = {} #self.color_mapper.map(node_identifier)
        extra_args = {**color_spec, **kwargs}
        self.dot.subgraph(g.dot, **extra_args)

    def display(self):
        self.dot.render("./foo.gv", view=True)


def parse_and_display(parser, type_string):
    h = parser(type_string)
    builder = DotGraphBuilder()
    h.graph(builder)[0].display()
    return h

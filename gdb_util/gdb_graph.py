import gdb # for the test_graph
from .gdb_wedge import get_symbols
from .graph import DotGraphBuilder


class DotColorMapper:
    """
    Signals have priority. The highest priority signal that is set
    will dictate the color
    """
    signal_priority_map = (
        ("set_error","orangered"),
        ("set_stopped","lightgrey"),
        ("set_value","dodgerblue"),
        ("start","mediumseagreen"),
        ("eval_predicate", "tan"))
    
    def __init__(self, chain_name, frame):
        self.chain_name = chain_name
        self.frame = frame

    def map(self, node_identifier):
        if not node_identifier or not self.frame:
            return {}

        syms = get_symbols(**node_identifier)

        mapped_color = 'ghostwhite'
        for (sig, color) in self.signal_priority_map:
            sig_values = [s.get_value(self.frame) for s in syms if s.signal_name == sig]
            #print(", ".join([f"{type(s)}: {s}" for s in sig_values]))
            if any(sig_values):
                mapped_color = color
                break
        
        return {'style': 'filled', 'fillcolor': mapped_color}


class DotColorMapperInt:
    """
    Signals have priority. The highest priority signal that is set
    will dictate the color
    """
    signal_priority_map = (
        ("set_error","orangered"),
        ("set_stopped","lightgrey"),
        ("set_value","dodgerblue"),
        ("start","mediumseagreen"),
        ("eval_predicate", "tan"))

    def __init__(self, chain_name, frame):
        self.chain_name = chain_name
        self.frame = frame

    def map(self, node_identifier):
        if not node_identifier or not self.frame:
            return {}

        syms = get_symbols(**node_identifier)

        mapped_color = 'ghostwhite'
        for (sig, color) in self.signal_priority_map:
            sig_values = [s.get_value(self.frame) for s in syms if s.signal_name == sig]
            if any(sig_values):
                mapped_color = color
                break
        
        return {'style': 'filled', 'fillcolor': mapped_color}


def test_graph(handles):
    f = gdb.selected_frame()
    g = DotGraphBuilder(color_mapper=DotColorMapper("sender chains", f))

    for h in handles:
        sub = g.subgraph(h.chain_name, h.chain_name)
        h.handled.graph(sub)
        g.add_subgraph(sub)

    g.display()

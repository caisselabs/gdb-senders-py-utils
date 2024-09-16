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

        syms = get_symbols(self.chain_name, **node_identifier)

        mapped_color = 'ghostwhite'
        for (sig, color) in self.signal_priority_map:
            sig_values = [s.get_value(self.frame) for s in syms if s.signal_name == sig]
            #print(", ".join([f"{type(s)}: {s}" for s in sig_values]))
            if any(sig_values):
                mapped_color = color
                break
        
        return {'style': 'filled', 'fillcolor': mapped_color}
        

def test_graph(h):
    f = gdb.selected_frame()
    h.handled.graph(DotGraphBuilder(color_mapper=DotColorMapper(h.chain_name, f)))[0].display()
    

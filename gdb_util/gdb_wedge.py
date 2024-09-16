import gdb
import re
import cxxfilt
from . import stdx
from . import handled

class Handled:
    # symbol_name is demangled
    def __init__(self, symbol_name):
        self.sym = stdx.prettify_ct_strings(symbol_name) #, pre="ct_string<", post=">")
        self.handled = handled.parse(self.sym)
        self.gdb_symbol = None
        self.chain_name = self.handled.chain_name

    def set_gdb_symbol(self, s):
        self.gdb_symbol = s

    def chain_name(self):
        return self.handled.chain_name

    def link_name(self):
        return self.handled.chain_name

    def signal_name(self):
        return self.handled.chain_name


handled_identity_re = re.compile(r'^async_trace::handled<\"(.+?)\", \"(.+?)\", \"(.+?)\", async_trace::context<async_trace::(.+?)_t,')


class ChainDebugSymbol:
    def __init__(self, gdb_symbol=None, pretty_name=None, chain_name=None, link_name=None, signal_name=None, sender_type=None):
        self.gdb_symbol = gdb_symbol
        self.pretty_name = pretty_name
        self.chain_name = chain_name
        self.link_name = link_name
        self.signal_name = signal_name
        self.sender_type = sender_type

    def get_value(self, frame):
        if not self.gdb_symbol or not frame:
            return None

        return self.gdb_symbol.value(frame)
        

class SymbolMapper:

    def __init__(self):
        self.chain_dict = {}

    def add_symbol(self, symbol):
        demangled_name = cxxfilt.demangle(symbol.name)
        pretty_name = stdx.prettify_ct_strings(demangled_name)

        m = re.match(handled_identity_re, pretty_name)
        if not m:
            # TODO: throw here?
            return None

        link_symbol = ChainDebugSymbol(symbol, pretty_name, *m.group(1, 2, 3, 4))

        l = self.chain_dict.get(link_symbol.chain_name, [])
        l.append(link_symbol)
        self.chain_dict[link_symbol.chain_name] = l

        return link_symbol

    
    def get_symbols(self, chain_name, link_name=None, signal_name=None, sender_type=None, sink_type=None):

        def keep_symbol(sym):
            if link_name and link_name != sym.link_name:
                return False
            if signal_name and signal_name != sym.signal_name:
                return False
            if sender_type and sender_type != sym.sender_type:
                return False
            if sink_type and sink_type != sym.sink_type:
                return False
            return True

        l = self.chain_dict.get(chain_name, [])
        
        return [s for s in l if keep_symbol(s)]
    
        


_symbol_mapper = SymbolMapper()


# --------------------------------------------------
def add_symbol(symbol):
    return _symbol_mapper.add_symbol(symbol)


# --------------------------------------------------
def get_symbols(chain_name, **kwargs):
    return _symbol_mapper.get_symbols(chain_name, **kwargs)


# --------------------------------------------------
def async_debug():
    async_debug_re = re.compile(r"async_trace::handled")
    #start_detached_op_state_re = re.compile(r"async::_start_detached::op_state")
    start_detached_op_state_re = re.compile(r"async_trace::context<async_trace::start_detached_t")
    
    frame = gdb.selected_frame()
    block = frame.block()
    debug_symbols = set()
    
    while block:
        for symbol in block:
            name = symbol.name
            demangled_name = cxxfilt.demangle(name)
            if async_debug_re.match(demangled_name):
                debug_symbols.add((symbol, demangled_name))
                    
        block = block.superblock

    handled_states = []
    
    for (debug_symbol, demangled_name) in debug_symbols:
        pretty_name = stdx.prettify_ct_strings(demangled_name)
        #print('prettify: {}'.format(pretty_name))
        # print('  ======== {}'.format(debug_symbol.value(frame)))
        add_symbol(debug_symbol)
        if start_detached_op_state_re.search(pretty_name):
            #print(f'found a start_detached.')
            try:
                h = Handled(pretty_name)
                h.set_gdb_symbol(debug_symbol)
                handled_states.append(h)
            except:
                pass
    return handled_states
        

def pretty_print(s):
    demangled_name = cxxfilt.demangle(s)
    pretty_name = stdx.prettify_ct_strings(demangled_name)
    print(pretty_name)
    



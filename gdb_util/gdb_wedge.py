import gdb
import re
import cxxfilt
from . import stdx
from . import handled


handled_chain_name_re = re.compile(r'^async_trace::handled<\"(.+?)\",')
handled_identity_re = re.compile(r'^async_trace::handled<\"(.+?)\", \"(.+?)\", \"(.+?)\", async::_(.+?)::')
handled_identity_ctx_re = re.compile(r'^async_trace::handled<\"(.+?)\", \"(.+?)\", \"(.+?)\", async_trace::context<async_trace::(.+?)_t,')


class Handled:
    # symbol_name is demangled
    def __init__(self, symbol_name):
        self.sym = stdx.prettify_ct_strings(symbol_name) #, pre="ct_string<", post=">")
        # need to extract the chain name early for the parser transformer
        m = re.match(handled_chain_name_re, self.sym)
        self.chain_name = m.group(1) if m else None
        self.handled = handled.parse(chain_name=self.chain_name, type_string=self.sym)
        self.gdb_symbol = None
        #self.chain_name = self.handled.chain_name

    def set_gdb_symbol(self, s):
        self.gdb_symbol = s

    def chain_name(self):
        return self.handled.chain_name

    def link_name(self):
        return self.handled.chain_name

    def signal_name(self):
        return self.handled.chain_name



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

        m0 = re.match(handled_identity_re, pretty_name)
        m1 = re.match(handled_identity_ctx_re, pretty_name)
        if not (m0 or m1):
            print(f"failed to add symbol to SymbolMapper: {pretty_name}")
            return None

        m = m1.group(1, 2, 3, 4) if m1 else m0.group(1, 2, 3, 4)
        link_symbol = ChainDebugSymbol(symbol, pretty_name, *m)

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
def async_debug(debug_flag=None):
    async_debug_re = re.compile(r"async_trace::handled")
    start_detached_op_state_re = re.compile(r'^async_trace::handled<\"(.+?)\", \"(.+?)\", \"start\", async::_start_detached::op_state')
    start_detached_context_re = re.compile(r'^async_trace::handled<\"(.+?)\", \"(.+?)\", \"start\", async_trace::context<async_trace::start_detached_t')
    frame = gdb.selected_frame()
    block = frame.block()
    debug_symbols = set()
    
    while block:
        for symbol in block:
            name = symbol.name
            demangled_name = cxxfilt.demangle(name)
            pretty_name = stdx.prettify_ct_strings(demangled_name)
            # if debug_flag:
            #     print(f"checking symbol {pretty_name[:50]}")
            if async_debug_re.search(pretty_name):
                if debug_flag:
                   print(f"have debug symbol: {pretty_name[:100]}")
                debug_symbols.add((symbol, pretty_name))
                    
        block = block.superblock

    handled_states = []

    
    for (debug_symbol, demangled_name) in debug_symbols:
        add_symbol(debug_symbol)
        if start_detached_op_state_re.search(demangled_name) or \
           start_detached_context_re.search(demangled_name):
            
            if debug_flag:
                print(f'found a start_detached: {demangled_name[:100]}')
            try:
                h = Handled(demangled_name)
                h.set_gdb_symbol(debug_symbol)
                handled_states.append(h)
            except:
                print("  --- error creating handled object for start_detached")
                print(f"      symbol: {demangled_name}")

    print(f"Found {len(debug_symbols)} debug symbols and {len(handled_states)} chains.")
    return handled_states
        

def pretty_print(s):
    demangled_name = cxxfilt.demangle(s)
    pretty_name = stdx.prettify_ct_strings(demangled_name)
    print(pretty_name)
    



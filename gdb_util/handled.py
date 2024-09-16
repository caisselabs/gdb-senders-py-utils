from pathlib import Path
from lark import Lark, Transformer
from gdb_util.sender import OpType, Context, ThenSender, SeqSender, JustSender, WhenAllSender, RepeatSender

# cache the parser
_handled_lark_parser = None


class HandledTransformer(Transformer):
    """A lark.Transformer for handled data types"""
    def handled_type(self, arg):
        return Handled(*arg)

    def string(self, s):
        (s,) = s
        return s[1:-1]

    #def integral(self, i):
    #    return int(i)

    def op_type(self, arg):
        return OpType(*arg)

    def context(self, arg):
        return Context(*arg)

    def then_sender_type(self, arg):
        return ThenSender(*arg)

    def seq_sender_type(self, arg):
        return SeqSender(*arg)

    def just_sender_type(self, arg):
        return JustSender(*arg)

    def when_all_sender_type(self, arg):
        return WhenAllSender(*arg)

    def repeat_sender_type(self, arg):
        return RepeatSender(*arg)


class Handled:
    def __init__(self, chain, link, signal, op):
        self.chain_name = chain
        self.link_name = link
        self.signal_name = signal
        self.op = op

    def chain(self):
        return self.op.sender.chain()

    def graph(self, builder):
        return (self.op.graph(builder)[0], None)

    
def parse(type_string):
    global _handled_lark_parser
    if not _handled_lark_parser:
        with open(Path(__file__).parent.absolute() / "handled.lark") as f:
            _handled_lark_parser = Lark(f, start="handled_type")

    tree = _handled_lark_parser.parse(type_string)
    return HandledTransformer().transform(tree)


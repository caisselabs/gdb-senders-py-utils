
class OpType:
    sender_type = "op"

    def __init__(self, label, sender, *args):
        self.label = label
        self.sender = sender

    def graph(self, builder):
        return (self.sender.graph(builder)[0], None)

class Context:
    sender_type = "context"

    def __init__(self, tag, label, sender, *args):
        self.tag = tag
        self.label = label
        self.sender = sender

    def graph(self, builder):
        return (self.sender.graph(builder)[0], None)

class ThenSender:
    sender_type = "then"

    def __init__(self, link, channel, sender, *args):
        self.link_name = link
        self.channel = channel
        self.sender = sender
        self.node_identifier = {"link_name": link, "sender_type": self.sender_type}

    def chain(self):
        return f"{self.sender.chain()} -> then({self.link_name})"

    def graph(self, builder):
        (builder, prev_end_node) = self.sender.graph(builder)
        node = f"then<{self.link_name}>"
        builder.add_node(name=node, label=f"then<{self.link_name}>", node_identifier=self.node_identifier)
        builder.add_edge(prev_end_node, node)
        return (builder, node)

class SeqSender:
    sender_type = "sequence"

    def __init__(self, link, sender_a, sender_b):
        self.link_name = link
        self.sender_a = sender_a
        self.sender_b = sender_b
        self.node_identifier = {"link_name": link, "sender_type": self.sender_type}

    def chain(self):
        return f"{self.sender_a.chain()} -> {self.sender_b.chain()}"

    def graph(self, builder):
        sender_a_name = f"seq<{self.link_name}, a>"
        sender_b_name = f"seq<{self.link_name}, b>"

        sub_a = builder.subgraph(sender_a_name)
        sub_b = builder.subgraph(sender_b_name)

        self.sender_a.graph(sub_a)
        self.sender_b.graph(sub_b)

        builder.add_subgraph(sub_a)
        builder.add_subgraph(sub_b)

        builder.add_edge(sender_a_name, sender_b_name, ltail=f"cluster_{sender_a_name}", lhead=f"cluster_{sender_b_name}")
        
        return (builder, sender_b_name)

class JustSender:
    sender_type = "just"

    def __init__(self, link, channel, *args, **kwargs):
        self.link_name = link
        self.channel = channel
        self.node_identifier = {"link_name": link, "sender_type": self.sender_type}

    def chain(self):
        return f"just({self.link_name})"

    def graph(self, builder):
        node_name = f"just<{self.link_name}>"
        builder.add_node(name=node_name, label=f"just<{self.link_name}>", node_identifier=self.node_identifier)
        return (builder, node_name)

class WhenAllSender:
    sender_type = "when_all"

    def __init__(self, link, *senders):
        self.link_name = link
        self.senders = senders[::2]
        self.node_identifier = {"link_name": link, "sender_type": "when_all"}
        
    def chain(self):
        ss = ", ".join([s.chain() for s in self.senders])
        return f"when_all[{ss}]"

    def graph(self, builder):
        when_all_name = f"when_all<{self.link_name}>"
        when_all_subgraph = builder.subgraph(when_all_name, node_identifier=self.node_identifier)

        for s in self.senders:
            s.graph(when_all_subgraph)

        builder.add_subgraph(when_all_subgraph, node_identifier=self.node_identifier)
        return (builder, when_all_name)

class RepeatSender:
    sender_type = "repeat"

    def __init__(self, link, sender, *args):
        self.link_name = link
        self.sender = sender
        self.node_identifier = {"link_name": link, "sender_type": "repeat"}
        
    def chain(self):
        ss = ", ".join([s.chain() for s in self.senders])
        return f"when_all[{ss}]"

    def graph(self, builder):
        (builder, prev_end_node) = self.sender.graph(builder)
        node = f"repeat<{self.link_name}>"
        builder.add_node(name=node, label=f"repeat<{self.link_name}>", node_identifier=self.node_identifier)
        builder.add_edge(prev_end_node, node)
        return (builder, node)


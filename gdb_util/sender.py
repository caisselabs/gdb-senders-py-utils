
class OpType:
    sender_type = "op"

    def __init__(self, chain_name, label, sender, *args):
        self.chain_name = chain_name
        self.label = label
        self.sender = sender

    def graph(self, builder):
        return (self.sender.graph(builder)[0], None)

class Context:
    sender_type = "context"

    def __init__(self, chain_name, tag, label, sender, *args):
        self.chain_name = chain_name
        self.tag = tag
        self.label = label
        self.sender = sender

    def graph(self, builder):
        return (self.sender.graph(builder)[0], None)

class ThenSender:
    sender_type = "then"

    def __init__(self, chain_name, link, channel, sender, *args):
        self.chain_name = chain_name
        self.link_name = link
        self.channel = channel
        self.sender = sender
        self.node_identifier = {"chain_name": chain_name,
                                "link_name": link,
                                "sender_type": self.sender_type}

    def chain(self):
        return f"{self.sender.chain()} -> then({self.link_name})"

    def graph(self, builder):
        (builder, prev_end_node) = self.sender.graph(builder)
        label_name = f"then<{self.link_name}>"
        node_name = f"{self.chain_name}-{label_name}"
        builder.add_node(name=node_name, label=label_name, node_identifier=self.node_identifier)
        builder.add_edge(prev_end_node, node_name)
        return (builder, node_name)

class SeqSender:
    sender_type = "sequence"

    def __init__(self, chain_name, link, sender_a, sender_b):
        self.chain_name = chain_name
        self.link_name = link
        self.sender_a = sender_a
        self.sender_b = sender_b
        self.node_identifier = {"chain_name": chain_name, "link_name": link, "sender_type": self.sender_type}

    def chain(self):
        return f"{self.sender_a.chain()} -> {self.sender_b.chain()}"

    def graph(self, builder):
        sender_a_label = f"seq<{self.link_name}, a>"
        sender_b_label = f"seq<{self.link_name}, b>"
        sender_a_name = f"{self.chain_name}-{sender_a_label}"
        sender_b_name = f"{self.chain_name}-{sender_b_label}"

        sub_a = builder.subgraph(sender_a_name, sender_a_label)
        sub_b = builder.subgraph(sender_b_name, sender_b_label)

        self.sender_a.graph(sub_a)
        self.sender_b.graph(sub_b)

        builder.add_subgraph(sub_a)
        builder.add_subgraph(sub_b)

        builder.add_edge(sender_a_name, sender_b_name, ltail=f"cluster_{sender_a_name}", lhead=f"cluster_{sender_b_name}")
        
        return (builder, sender_b_name)

class JustSender:
    sender_type = "just"

    def __init__(self, chain_name, link, channel, *args, **kwargs):
        self.chain_name = chain_name
        self.link_name = link
        self.channel = channel
        self.node_identifier = {"chain_name": chain_name, "link_name": link, "sender_type": self.sender_type}

    def chain(self):
        return f"just({self.link_name})"

    def graph(self, builder):
        label = f"just<{self.link_name}>"
        node_name = f"{self.chain_name}-{label}"
        builder.add_node(name=node_name, label=label, node_identifier=self.node_identifier)
        return (builder, node_name)

class WhenAllSender:
    sender_type = "when_all"

    def __init__(self, chain_name, link, *senders):
        self.chain_name = chain_name
        self.link_name = link
        self.senders = senders[::2]
        self.node_identifier = {"chain_name": chain_name, "link_name": link, "sender_type": "when_all"}
        
    def chain(self):
        ss = ", ".join([s.chain() for s in self.senders])
        return f"when_all[{ss}]"

    def graph(self, builder):
        node_label = f"when_all<{self.link_name}>"
        node_name = f"{self.chain_name}-{node_label}"
        when_all_subgraph = builder.subgraph(node_name, node_label, node_identifier=self.node_identifier)

        for s in self.senders:
            s.graph(when_all_subgraph)

        builder.add_subgraph(when_all_subgraph, node_identifier=self.node_identifier)
        return (builder, node_name)

class RepeatSender:
    sender_type = "repeat"

    def __init__(self, chain_name, link, sender, *args):
        self.chain_name = chain_name
        self.link_name = link
        self.sender = sender
        self.node_identifier = {"chain_name": chain_name, "link_name": link, "sender_type": "repeat"}
        
    def chain(self):
        ss = ", ".join([s.chain() for s in self.senders])
        return f"repeat[{ss}]"

    def graph(self, builder):
        node_label = f"repeat<{self.link_name}>"
        node_name = f"{self.chain_name}-{node_label}"
        repeat_subgraph = builder.subgraph(node_name, node_label, node_identifier=self.node_identifier, style='rounded')

        self.sender.graph(repeat_subgraph)

        builder.add_subgraph(repeat_subgraph, node_identifier=self.node_identifier)
        return (builder, node_name)

    

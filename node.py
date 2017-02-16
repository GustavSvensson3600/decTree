class Node:
    pass

class TreeNode(Node):
    def __init__(self, attribute, label):
        self.attribute = attribute
        self.label = label
        self.children = list()

    def add_child(self, child):
        self.children.append(child)

    def print_deep(self, depth, parent):
        print "\t" * depth, parent.name, "=", self.label
        for child in self.children:
            child.print_deep(depth+1, self.attribute)

    def print_node(self):
        for child in self.children:
            child.print_deep(0, self.attribute)

class LeafNode(Node):
    def __init__(self, attribute, label, klass):
        self.attribute = attribute
        self.label = label
        self.klass = klass

    def print_deep(self, depth, parent):
        print "\t" * depth,self.attribute.name, "=", self.label + ":", self.klass
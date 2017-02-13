class Node:
    pass

class TreeNode(Node):
    def __init__(self, attribute, label):
        self.attribute = attribute
        self.label = label
        self.children = list()

    def add_child(self, child):
        self.children.append(child)

    def print_node(self, depth = 0):
        print "\t" * depth, self.attribute.name, "=", self.label
        for child in self.children:
            child.print_node(depth+1)

class LeafNode(Node):
    def __init__(self, attribute, label, klass):
        self.attribute = attribute
        self.label = label
        self.klass = klass

    def print_node(self, depth):
        print "\t" * depth, self.attribute.name, "=", self.label, ":", self.klass

class Attr:
    def __init__(self,name):
        self.name = name

a = Attr("A")
b = Attr("B")
root = TreeNode(a, "1")
root.add_child(LeafNode(b, "1", "YES"))
root.add_child(LeafNode(b, "2", "NO"))
root.print_node()
from math import log
import string
import node
import argparse

class Attr:
    def __init__(self, line):
        self.line_ = line

        attr_list = line.index(' ', 11) + 1
        self.name = line[11:attr_list-1]
        self.values = set()

        self.type = "enum"

        if line[attr_list] == '{':
            end = line.index('}')
            self.values = set([x.strip() for x in line[attr_list+1:end].split(',')])
        else:
            # TODO: string, date, real/int/numeric
            self.type = "numeric"

    def offer(self, value):
        self.values.add(value)

    def is_numeric(self):
        return self.type == "numeric"

    def __repr__(self):
        return self.name + ": " + self.values.__repr__()

class EntryData:
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value

    def is_attr(self, attr):
        return self.attr.name == attr.name

    def __repr__(self):
        return self.value

class Entry:
    def __init__(self, line, attrs):
        self.line_ = line

        self.attrs = list()

        token_beg = 0
        token_end = line.index(',')

        for attr in attrs:
            token = line[token_beg:token_end].strip()

            token_beg = token_end + 1
            token_end = line.find(',', token_beg)
            if token_end == -1:
                token_end = len(line)

            self.attrs.append(EntryData(attr, token))

    def classified(self, eattr):
        for attr in self.attrs:
            # attr.attr.name == eattr.attr.name
            if attr.is_attr(eattr.attr):
                return attr.value == eattr.value
        return False

    def __repr__(self):
        return self.attrs.__repr__()

def split(dataset, attr, value):
    eattr = EntryData(attr, value)
    return [x for x in dataset if x.classified(eattr)]

def entropy(dataset, target_attr):
    if len(dataset) == 0:
        return 0

    total_entropy = 0
    for label in target_attr.values:
        freq = len(split(dataset, target_attr, label))
        px = freq / float(len(dataset))
        if freq != 0:
            total_entropy = total_entropy - px * log(px, 2)

    return total_entropy

def pick_attr(dataset, target_attr, available_attr):
    """ Pick the attribute from available_attr that results
        in the maximal information gain with respect to target_attr.
    """
    n_dataset = float(len(dataset))
    before = entropy(dataset, target_attr)
    best_attri = available_attr[0]
    best_gain = 0
    #print "--- NEW ROUND ---"
    for attr in available_attr:
        attr_gain = before
        for label in attr.values:
            split_dataset = split(dataset, attr, label)
            e = entropy(split_dataset, target_attr)
            gain = - (len(split_dataset) / n_dataset) * e
            attr_gain += gain
        if attr_gain > best_gain:
            best_attri = attr
            best_gain = attr_gain
    #    print "Attribute : ", attr, " : ", attr_gain
    return best_attri

def find_optimal_label(dataset, target_attr):
    """ Find the most common label in the dataset """
    best_value = target_attr.values.pop()
    best_cmp = len(split(dataset, target_attr, best_value))
    target_attr.values.add(best_value)

    for value in target_attr.values:
        split_set = split(dataset, target_attr, value)
        if len(split_set) > best_cmp:
            best_value = value
            best_cmp = len(split_set)
    return best_value

def ID3_init(dataset, target_attr, initial_attrs):
    """ Use a dummy root node attribute because of our strange tree """
    initial_attrs.remove(target_attr)
    fake_attr = Attr("@attribute root {root}")
    return ID3(dataset, target_attr, initial_attrs, fake_attr, "root")

def ID3(dataset, target_attr, remaining_attr, parent_attr, branch_label):
    """ Recursively create an ID3. Rememeber the parent and branch so
        that we can print the tree.
    """
    # We can terminate if the dataset is fully classified
    for value in target_attr.values:
        split_set = split(dataset, target_attr, value)
        if len(split_set) == len(dataset):
            return node.LeafNode(parent_attr, branch_label, value)

    # If no attributes remain then ask the dataset which label is best classified
    if len(remaining_attr) == 0:
        label = find_optimal_label(dataset, target_attr)
        return node.LeafNode(parent_attr, branch_label, label)

    # Pick best attribute according to information gain
    best_attr = pick_attr(dataset, target_attr, remaining_attr)
    remaining_attr.remove(best_attr)

    # Create new tree rooted at selected attribute
    root = node.TreeNode(best_attr, branch_label)
    for label in best_attr.values:
        split_dataset = split(dataset, best_attr, label)
        if len(split_dataset) == 0:
            best_label = find_optimal_label(dataset, target_attr)
            root.add_child(node.LeafNode(best_attr, label, best_label))
        else:
            root.add_child(ID3(split_dataset, target_attr, remaining_attr, best_attr, label))

    return root

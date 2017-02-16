from math import log
import string
import node


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
    
    def is_str(self):
        return self.type == "string"

    def is_enum(self):
        return self.type == "enum"

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
            token = line[token_beg:token_end]
            
            if attr.is_numeric():
                attr.offer(token)

            token_beg = token_end + 1
            token_end = line.find(',', token_beg)
            if token_end == -1:
                token_end = len(line)

            self.attrs.append(EntryData(attr, token))

    def classified(self, eattr):
        for attr in self.attrs:
            if attr.is_attr(eattr.attr):
                return attr.value == eattr.value
        return False

def split(set, attr, value):
    eattr = EntryData(attr, value)
    return [x for x in set if x.classified(eattr)]

def entropy(set, target_attr):
    if len(set) == 0:
        return 0

    labels = {}
    for label in target_attr.values:
        labels[label] = 0

    # count
    for entry in set:
        for label in target_attr.values:
            if entry.classified(EntryData(target_attr, label)):
                labels[label] = labels[label] + 1
    
    # probabilities: px(i)
    for label in labels:
        count = labels[label]
        labels[label] = count / float(len(set))

    total_entropy = 0
    for label in labels:
        px = labels[label]
        entropy = 0
        if px != 0:
            entropy = - px * log(px, 2)
        total_entropy = total_entropy + entropy
    
    return total_entropy

def pick_attr(dataset, target_attr, availible_attr):
    """ Pick the attribute from available_attr that results
        in the maximal information gain with respect to target_attr.
    """
    items = len(dataset)
    before = entropy(dataset, target_attr)
    best_attri = attrs[0]
    best_gain = 0

    for attr in availible_attr:
        attr_gain = before
        for label in attr.values:
            split_dataset = split(dataset, attr, label)
            e = entropy(split_dataset, target_attr)
            gain = - (len(split_dataset) / float(items)) * e
            attr_gain += gain
        if attr_gain > best_gain:
            best_attri = attr
            best_gain = attr_gain
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
            best_value = find_optimal_label(dataset, target_attr)
            root.add_child(node.LeafNode(best_attr, label, best_value))
        else:
            root.add_child(ID3(split_dataset, target_attr, remaining_attr, best_attr, label))
    
    return root

with open("weather.nominal.arff") as f:
    content = f.readlines()

    content = [x.strip() for x in content if x.strip() != '']

    nodes = list()
    attrs = list()
    
    # @relation <>
    # @attribute <> <>
    # @data
    for line in content:
        if line.find("@relation") != -1:
            pass
        elif line.find("@attribute") != -1:
            attrs.append(Attr(line))
        elif line.find("@data") != -1:
            pass
        elif line.find("%") != -1:
            pass
        else:
            nodes.append(Entry(line, attrs))

    play = attrs[-1]
    root = ID3_init(nodes, play, attrs)
    root.print_node()
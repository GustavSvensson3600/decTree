from math import log
import string
import node

content = list()

with open("weather.arff") as f:
    content = f.readlines()

content = [x.strip() for x in content if x.strip() != ''] 

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

        print self.name, self.values

    def offer(self, value):
        self.values.add(value)

    def is_numeric(self):
        return self.type == "numeric"
    
    def is_str(self):
        return self.type == "string"

    def is_enum(self):
        return self.type == "enum"

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
    before = entropy(nodes, target_attr)
    best_attri = attrs[0]
    best_gain = 0

    for attr in availible_attr:
        attr_count = len(nodes)
        attr_gain = before
        for label in attr.values:
            dataset = split(nodes, attr, label)
            e = entropy(dataset, target_attr)
            gain = - (len(dataset) / float(attr_count)) * e
            attr_gain += gain
        if attr_gain > best_gain:
            best_attri = attr
            best_gain = attr_gain
    return best_attri
            #print attr.name, label, e, gain, len(dataset)


def ID3(dataset, target_attr, remaining_attr, parent_attr, branch_label):
    if len(dataset) == 0:
        # no dataset :(
        pass
    for value in target_attr.values:
        split_set = split(dataset, target_attr, value)
        if len(split_set) == len(dataset):
            # value classifies whole dataset
            return node.LeafNode(parent_attr, branch_label, value)
    if len(remaining_attr) == 0:
        best_value = target_attr.values[0]
        best_cmp = len(split(dataset, target_attr, best_value))
        for value in target_attr.values:
            split_set = split(dataset, target_attr, value)
            if len(split_set) > best_cmp:
                best_value = value
                best_cmp = len(split_set)
        return node.LeafNode(parent_attr,branch_label,best_value)
    best_attr = pick_attr(dataset,target_attr,remaining_attr)
    root = node.TreeNode(best_attr, branch_label)
    for label in best_attr.values:
        split_dataset = split(nodes, attr, label)
        if len(split_dataset) == 0:
            #Then below this new branch add a leaf node with label = most common target value in the examples
            best_value = target_attr.values[0]
            #So question is if split_dataset or dataset should be used, read above comment
            #They seemed to use the convention examples[a_i] for split dataset
            #Which would imply the unsplit one, but that seems strange so ?
            best_cmp = len(split(split_dataset, target_attr, best_value))
            for value in target_attr.values:
                split_set = split(split_dataset, target_attr, value)
                if len(split_set) > best_cmp:
                    best_cmp = len(split_set)
                    best_value = value
            root.add_child(node.LeafNode(best_attr, label, best_value))
        else:
            remaining_attr.remove(best_attr)
            print 'best attribute: ', best_attr.name, ' remanining is ', remaining_attr
            root.add_child(ID3(split_dataset, target_attr, remaining_attr, best_attr, label))

# @relation <>
# @attribute <> <>
# @data
nodes = list()
attrs = list()
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
before = entropy(nodes, play)
print 'before', before
for attr in attrs:
    if attr == play:
        continue
    
    attr_count = len(nodes)
    attr_gain = before
    for label in attr.values:
        dataset = split(nodes, attr, label)
        e = entropy(dataset, play)
        gain = - (len(dataset) / float(attr_count)) * e
        attr_gain += gain
        #print attr.name, label, e, gain, len(dataset)

    print attr.name, attr_gain
attrs.remove(attrs[-1])
root = ID3(nodes, attrs[-1], attrs, "root", "root")

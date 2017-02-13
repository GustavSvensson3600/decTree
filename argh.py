from math import log
import string

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

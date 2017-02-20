import string
import node
import argparse
import dtl


parser = argparse.ArgumentParser(description="Create a decision tree using ID3")
parser.add_argument("--file", help="select your file", action="store", type=str, dest="file", default="restaurant.arff")
parser.add_argument("--target", help="select your target", action="store", type=str, dest="target", default="WillWait")
args = parser.parse_args()

with open(args.file) as f:
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
            attrs.append(dtl.Attr(line))
            if attrs[-1].name == args.target:
                target = attrs[-1]
        elif line.find("@data") != -1:
            pass
        elif line.find("%") != -1:
            pass
        else:
            nodes.append(dtl.Entry(line, attrs))

    root = dtl.ID3_init(nodes, target, attrs)
    root.print_node()
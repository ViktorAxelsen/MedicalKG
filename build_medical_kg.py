import json
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher


def get_noe4j(ip='http://10.103.11.105:7474', auth=("neo4j", "zhz"), empty=True):
    graph = Graph(ip, auth=auth)
    if empty:
        graph.delete_all()

    return graph


def read_data(data_path, type_path):
    with open(data_path, mode='r', encoding='utf-8') as f:
        raw = f.readlines()

    nodes = [json.loads(node) for node in raw]

    with open(type_path, mode='r', encoding='utf-8') as f:
        types = json.load(f)

    return nodes, types


def get_name_dict(nodes):
    name_list = dict()
    for ind, node in enumerate(nodes):
        if "name" in node.keys():
            name_list[node["name"]] = ind

    return name_list


def process(graph, nodes):
    node_list = []
    name_list = get_name_dict(nodes)
    rels = []
    for ind, node in enumerate(nodes):
        node_type = node['type']
        node_labels = [node_type]
        node_props = dict()
        # Append Meaningful Labels
        if node_type.endswith("类") or node_type.endswith("药品") or node_type.endswith("制剂"):
            node_labels.append("药物")
        elif node_type.endswith("作用"):
            node_labels.append("相互作用")
        # Filter Node Props
        for k, v in node.items():
            if v in name_list.keys():
                rels.append([ind, k, name_list[v]])
            node_props[k] = v
        graph_node = Node(*node_labels, **node_props)
        graph.create(graph_node)
        node_list.append(graph_node)

        if ind % 1000 == 0:
            print("{} Finished".format(ind))

    for rel in rels:
        graph.create(Relationship(node_list[rel[0]], rel[1], node_list[rel[2]]))


if __name__ == '__main__':
    graph = get_noe4j(ip='http://10.103.11.105:7474', auth=("neo4j", "zhz"), empty=True)
    nodes, types = read_data(data_path=r'C:\Users\10092\Downloads\data\processed.json',
                             type_path=r'C:\Users\10092\Downloads\data\type2attrib.json')
    process(graph, nodes)


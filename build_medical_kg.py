"""
导入Neo4j数据库
"""
import json
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher


def get_noe4j(ip='http://10.103.11.105:7474', auth=("neo4j", "zhz"), empty=False):
    """
    获取Neo4j数据库实例

    Args:
        ip (str): 数据库ip地址. Default: 'http://10.103.11.105:7474'.
        auth (tuple): 验证信息. Default: ("neo4j", "zhz").
        empty (bool): 是否清空数据库. Default: False.

    Returns:
        Neo4j数据库实例
    """
    graph = Graph(ip, auth=auth)
    if empty:
        graph.delete_all()

    return graph


def read_data(data_path, type_path):
    """
    读取数据

    Args:
        data_path (str): 数据路径
        type_path (str): 类型数据路径

    Returns:
        节点数据、类型数据
    """
    with open(data_path, mode='r', encoding='utf-8') as f:
        raw = f.readlines()

    nodes = [json.loads(node) for node in raw]

    with open(type_path, mode='r', encoding='utf-8') as f:
        types = json.load(f)

    return nodes, types


def get_name_dict(nodes):
    """
    构建节点“name”关系索引，加快节点关系构建速度

    Args:
        nodes (list): 节点列表

    Returns:
        “name”关系索引
    """
    name_list = dict()
    for ind, node in enumerate(nodes):
        if "name" in node.keys():
            name_list[node["name"]] = ind

    return name_list


def process(graph, nodes):
    """
    插入数据

    Args:
        graph: Neo4j数据库
        nodes (list): 节点列表
    """
    node_list = []
    name_list = get_name_dict(nodes)  # 获取”name“索引
    rels = []
    for ind, node in enumerate(nodes):
        node_type = node['type']
        node_labels = [node_type]
        node_props = dict()
        # 附加一些有意义的父类标签
        if node_type.endswith("类") or node_type.endswith("药品") or node_type.endswith("制剂"):
            node_labels.append("药物")
        elif node_type.endswith("作用"):
            node_labels.append("相互作用")
        # 过滤出节点的固有属性以及关系属性
        for k, v in node.items():
            # 若v存在于"name"索引中且当前节点index不等于”name“索引对应的值，则说明k代表一种关系，且不为自身（去除Self-Loop Relation）
            if v in name_list.keys() and ind != name_list[v]:
                rels.append([ind, k, name_list[v]])
                continue
            node_props[k] = v  # 固有属性
        graph_node = Node(*node_labels, **node_props)
        graph.create(graph_node)
        node_list.append(graph_node)

        if ind % 1000 == 0:
            print("{} Node Finished".format(ind))

    print("Total Relations: {}".format(len(rels)))
    for ind, rel in enumerate(rels):
        graph.create(Relationship(node_list[rel[0]], rel[1], node_list[rel[2]]))  # 创建关系

        if ind % 1000 == 0:
            print("{} Rels Finished".format(ind))


if __name__ == '__main__':
    graph = get_noe4j(ip='http://10.103.11.105:7474', auth=("neo4j", "zhz"), empty=False)
    nodes, types = read_data(data_path=r'C:\Users\10092\Downloads\data\processed.json',
                             type_path=r'C:\Users\10092\Downloads\data\type2attrib.json')
    process(graph, nodes)


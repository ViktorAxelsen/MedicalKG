"""
可视化
"""
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def check_rel(type):
    """
    检查类型字符串，进行合适的精简

    Args:
        type (str): 关系类型字符串

    Returns:
        精简后的关系类型字符串
    """
    if type.startswith("包含"):
        return "包含"
    elif type.startswith("来自"):
        return "来自"
    else:
        return type


def check_query(q):
    """
    检查查询q是否存在

    Args:
        q: 查询结果

    Returns:
        存在返回True；不存在返回False
    """
    if not q:
        print("No Match")
        return False
    else:
        return True


def parse(rels, from_list, to_list, rel_dict):
    """
    解析关系

    Args:
        rels: 关系列表
        from_list (list): 起始节点列表
        to_list (list): 终止节点列表
        rel_dict (dict): 关系类型字典

    Returns:
        起始节点列表，终止节点列表，关系类型字典
    """
    if not rels:
        return from_list, to_list, rel_dict
    for rel in rels:
        src = rel.start_node
        dst = rel.end_node
        from_list.append(src['name'])
        to_list.append(dst['name'])
        rel_dict[(src['name'], dst['name'])] = check_rel(type(rel).__name__)

    return from_list, to_list, rel_dict


def cut(from_list, to_list, rel_dict, limit):
    """
    截断以便于显示在一张图上不至于过于拥挤

    Args:
        from_list (list): 起始节点列表
        to_list (list): 终止节点列表
        rel_dict (dict): 关系类型字典
        limit (int): 最大显示关系数

    Returns:
        截断后的起始节点列表，终止节点列表，关系类型字典
    """
    from_list = from_list[:limit]
    to_list = to_list[:limit]
    to_remove = list(rel_dict.keys())[limit:]
    for key in to_remove:
        del rel_dict[key]

    return from_list, to_list, rel_dict


def visualize(graph, label_keyword, limit=10, r_dir='bi', r_type=None, **prop_keyword):
    """
    可视化符合条件的某个节点的知识图谱

    Args:
        graph: Neo4j数据库
        label_keyword (str): 待查询节点的label关键字
        limit (int): 最大显示关系数. Default: 10.
        r_dir (str): 关系方向，分为：“bi”：双向关系均可；“in”：仅入边关系；“out”：仅出边关系. Default: "bi".
        r_type: 关系类型. Default: None.
        **prop_keyword: 待查询节点的固有属性
    """
    # 查询出符合条件的节点
    if prop_keyword:
        q = graph.nodes.match(label_keyword).where(**prop_keyword).first()
    else:
        q = graph.nodes.match(label_keyword).first()

    if not check_query(q):
        return

    # 获取节点的关系
    out_rels = None
    in_rels = None
    if r_dir == 'bi':
        out_rels = list(RelationshipMatcher(graph).match([q], r_type=r_type))
        in_rels = list(RelationshipMatcher(graph).match([None, q], r_type=r_type))
    elif r_dir == 'in':
        in_rels = list(RelationshipMatcher(graph).match([None, q], r_type=r_type))
    elif r_dir == 'out':
        out_rels = list(RelationshipMatcher(graph).match([q], r_type=r_type))
    else:
        raise ValueError("r_dir should be within ['bi', 'in', 'out']")

    from_list = []
    to_list = []
    rel_dict = dict()

    # 解析关系，构建构图所需的列表以及关系字典
    from_list, to_list, rel_dict = parse(out_rels, from_list, to_list, rel_dict)
    from_list, to_list, rel_dict = parse(in_rels, from_list, to_list, rel_dict)
    from_list, to_list, rel_dict = cut(from_list, to_list, rel_dict, limit=limit)
    print(from_list)
    print(to_list)
    print(rel_dict)

    # 构图
    df = pd.DataFrame({'from': from_list, 'to': to_list})
    G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, edge_color='#87CEFA70', width=3.0,
            edge_cmap=plt.cm.Blues, arrows=True, font_size=10, arrowsize=15)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=rel_dict, font_size=10, rotate=False)
    plt.show()


def visualize_graph(from_list, to_list, rel_dict):
    """
    可视化查询知识图谱

    Args:
        from_list (list): 起始节点列表
        to_list (list): 终止节点列表
        rel_dict (dict): 关系类型字典
    """
    df = pd.DataFrame({'from': from_list, 'to': to_list})
    G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, edge_color='#87CEFA70', width=3.0,
            edge_cmap=plt.cm.Blues, arrows=True, font_size=10, arrowsize=15)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=rel_dict, font_size=10, rotate=False)
    plt.show()


if __name__ == '__main__':
    graph = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
    visualize(graph=graph, label_keyword="比索洛尔类", limit=10, r_dir='bi', r_type=None)
"""
信息统计
"""
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher


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


def count(graph, label_keyword, **prop_keyword):
    """
    根据给定参数统计节点信息

    Args:
        graph: Neo4j数据库
        label_keyword (str): 待查询节点的label关键字
        **prop_keyword: 待查询节点的固有属性

    Returns:
        符合要求的节点数量，节点实例列表
    """
    if prop_keyword:
        q = graph.nodes.match(label_keyword).where(**prop_keyword)
        print(q.count())
    else:
        q = graph.nodes.match(label_keyword)
        print(q.count())

    return q.count(), q.all()


def rel_count(graph, node, r_dir='bi', r_type=None):
    """
    根据给定参数统计关系信息

    Args:
        graph: Neo4j数据库
        node: 带查询的节点实例
        r_dir (str): 关系方向，分为：“bi”：双向关系均可；“in”：仅入边关系；“out”：仅出边关系. Default: "bi".
        r_type: 关系类型. Default: None.

    Returns:
        符合条件的关系数量
    """
    if not check_query(node):
        return
    node = node[0]
    out_rels = None
    in_rels = None
    count = 0
    if r_dir == 'bi':  # 双向关系则分别统计出和入关系
        out_rels = list(RelationshipMatcher(graph).match([node], r_type=r_type))
        in_rels = list(RelationshipMatcher(graph).match([None, node], r_type=r_type))
    elif r_dir == 'in':  # 入边关系
        in_rels = list(RelationshipMatcher(graph).match([None, node], r_type=r_type))
    elif r_dir == 'out':  # 出边关系
        out_rels = list(RelationshipMatcher(graph).match([node], r_type=r_type))
    else:
        raise ValueError("r_dir should be within ['bi', 'in', 'out']")

    count += len(out_rels)
    count += len(in_rels)

    print(count)

    return count


if __name__ == '__main__':
    graph = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
    node_ct, node = count(graph, label_keyword="比索洛尔类")
    rel_count(graph, node)
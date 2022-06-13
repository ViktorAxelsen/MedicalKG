from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher


def check_query(q):
    if not q:
        print("No Match")
        return False
    else:
        return True


def count(graph, label_keyword, **prop_keyword):
    if prop_keyword:
        q = graph.nodes.match(label_keyword).where(**prop_keyword)
        print(q.count())
    else:
        q = graph.nodes.match(label_keyword)
        print(q.count())

    return q.count(), q.all()


def rel_count(graph, node, r_dir='bi', r_type=None):
    if not check_query(node):
        return
    node = node[0]
    out_rels = None
    in_rels = None
    count = 0
    if r_dir == 'bi':
        out_rels = list(RelationshipMatcher(graph).match([node], r_type=r_type))
        in_rels = list(RelationshipMatcher(graph).match([None, node], r_type=r_type))
    elif r_dir == 'in':
        in_rels = list(RelationshipMatcher(graph).match([None, node], r_type=r_type))
    elif r_dir == 'out':
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
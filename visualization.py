import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def check_rel(type):
    if type.startswith("包含"):
        return "包含"
    elif type.startswith("来自"):
        return "来自"
    else:
        return type


def check_query(q):
    if not q:
        print("No Match")
        return False
    else:
        return True


def parse(rels, from_list, to_list, rel_dict):
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
    from_list = from_list[:limit]
    to_list = to_list[:limit]
    to_remove = list(rel_dict.keys())[limit:]
    for key in to_remove:
        del rel_dict[key]

    return from_list, to_list, rel_dict


def visualize(graph, label_keyword, limit=10, r_dir='bi', r_type=None, **prop_keyword):
    if prop_keyword:
        q = graph.nodes.match(label_keyword).where(**prop_keyword).first()
    else:
        q = graph.nodes.match(label_keyword).first()

    if not check_query(q):
        return

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

    from_list, to_list, rel_dict = parse(out_rels, from_list, to_list, rel_dict)
    from_list, to_list, rel_dict = parse(in_rels, from_list, to_list, rel_dict)
    from_list, to_list, rel_dict = cut(from_list, to_list, rel_dict, limit=limit)

    df = pd.DataFrame({'from': from_list, 'to': to_list})
    G = nx.from_pandas_edgelist(df, 'from', 'to', create_using=nx.DiGraph())
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=400, edge_color='#87CEFA70', width=3.0,
            edge_cmap=plt.cm.Blues, arrows=True, font_size=6, arrowsize=15)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=rel_dict, font_size=6, rotate=False)
    plt.show()


if __name__ == '__main__':
    graph = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
    visualize(graph=graph, label_keyword="比索洛尔类", limit=10, r_dir='bi', r_type=None)
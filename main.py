"""
入口文件
"""
import argparse
from py2neo import Graph
from visualization import visualize
from stat_count import count, rel_count
from qa import QA


if __name__ == '__main__':
    graph = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, default=1)
    parser.add_argument("--label_keyword", type=str, default="比索洛尔类")
    parser.add_argument("--r_dir", type=str, default="bi")
    parser.add_argument("--r_type", type=str, default=None)
    parser.add_argument("--cypher", type=str, default="MATCH (n: `比索洛尔类`) RETURN n")
    args, unknown = parser.parse_known_args()  # 解析已定义键值对参数
    extra_args = dict()
    for i, arg in enumerate(unknown):  # 解析未知键值对参数，作为节点的固有属性用于查询
        if arg.startswith("--"):
            extra_args[arg[2:]] = unknown[i + 1]
    print(args)
    print(extra_args)
    task = args.task
    if task == 1:
        QA()  # 问答系统
    elif task == 2:
        visualize(graph=graph,
                  label_keyword=args.label_keyword,
                  r_dir=args.r_dir,
                  r_type=args.r_type,
                  **extra_args)  # 可视化
    elif task == 3:
        count(graph=graph,
              label_keyword=args.label_keyword,
              **extra_args)  # 节点统计信息
    elif task == 4:
        node_ct, node = count(graph=graph,
                              label_keyword=args.label_keyword,
                              **extra_args)  # 关系统计信息
        rel_count(graph=graph,
                  node=node,
                  r_dir=args.r_dir,
                  r_type=args.r_type)
    elif task == 5:
        q = graph.run(args.cypher).data()  # Cypher查询
        print(q)
    else:
        QA()  # 问答系统

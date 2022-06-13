import argparse
from py2neo import Graph
from visualization import visualize
from stat_count import count, rel_count



if __name__ == '__main__':
    graph = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, default=1)
    parser.add_argument("--label_keyword", type=str, default="比索洛尔类")
    parser.add_argument("--r_dir", type=str, default="bi")
    parser.add_argument("--r_type", type=str, default=None)
    args, unknown = parser.parse_known_args()
    extra_args = dict()
    for i, arg in enumerate(unknown):
        if arg.startswith("--"):
            extra_args[arg[2:]] = unknown[i + 1]
    print(args)
    print(extra_args)
    task = args.task
    if task == 1:
        pass  # QA
    elif task == 2:
        visualize(graph=graph,
                  label_keyword=args.label_keyword,
                  r_dir=args.r_dir,
                  r_type=args.r_type,
                  **extra_args)  # Visualization
    elif task == 3:
        count(graph=graph,
              label_keyword=args.label_keyword,
              **extra_args)  # Stat Node
    elif task == 4:
        node_ct, node = count(graph=graph,
                              label_keyword=args.label_keyword,
                              **extra_args)  # Stat Rel
        rel_count(graph=graph,
                  node=node,
                  r_dir=args.r_dir,
                  r_type=args.r_type)
    elif task == 5:
        pass  # Cypher Query
    else:
        pass  # QA
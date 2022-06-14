#!/usr/bin/env python3
# coding: utf-8
# File: answer_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-5

from py2neo import Graph, NodeMatcher, RelationshipMatcher

class AnswerSearcher:
    def __init__(self):
        self.g = Graph('http://10.103.11.105:7474', auth=("neo4j", "zhz"))
        self.num_limit = 20
        self.node_matcher = NodeMatcher(self.g)
        self.rel_matcher = RelationshipMatcher(self.g)

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, queries):
        answers = []
        for query in queries:
            ress = self.g.evaluate(query)
            if ress:
                answers.append(ress)
            # final_answer = self.answer_prettify(question_type, answers)
            # if final_answer:
            #     final_answers.append(final_answer)
        # print("searched:", answers)
        return answers
    
    def match_node(self, node_type="", **prop):
        if prop:
            q = self.node_matcher.match(node_type).where(**prop)
        else:
            q = self.node_matcher.match(node_type)
        return list(q)
    
    def match_rel(self, node1=None, node2=None, rel_type=None):
        q = self.rel_matcher.match((node1, node2), r_type=rel_type)
        return list(q)
    
    def get_valid_start_node(self, end_node, rel_type=None, node_type=None):
        nodes = []
        if rel_type is None or not isinstance(rel_type, list):
            nodes += self.match_rel(node1=None, node2=end_node, rel_type=rel_type)
        else:
            for r in rel_type:
                nodes += self.match_rel(node1=None, node2=end_node, rel_type=r)
        nodes = [r.start_node for r in nodes]
        # print([str(n.labels) for n in nodes])
        if node_type:
            nodes = [n for n in nodes if any([t in n.labels for t in node_type])]
        return nodes
    
    def get_valid_end_node(self, start_node, rel_type=None, node_type=None):
        nodes = []
        if rel_type is None or not isinstance(rel_type, list):
            nodes += self.match_rel(node1=start_node, node2=None, rel_type=rel_type)
        else:
            for r in rel_type:
                nodes += self.match_rel(node1=start_node, node2=None, rel_type=r)
        nodes = [r.end_node for r in nodes]
        if node_type:
            nodes = [n for n in nodes if any([t in n.labels for t in node_type])]
        return nodes






if __name__ == '__main__':
    searcher = AnswerSearcher()
    q = searcher.match_node(name="药药相互作用977")
    # q = searcher.match_rel(node1=q, rel_type="有无相互作用存在")
    print(q)

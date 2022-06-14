#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4
from answer_search import AnswerSearcher

def handle(text):
    for i in "01234567890.、，。,":
        text = text.strip(i)
    return text.strip()

class QuestionParser:
    def __init__(self):
        self.searcher = AnswerSearcher()

    def parser_main(self, res_classify):
        entity_dict = res_classify['args']
        question_types = res_classify['question_types']
        answers = []
        for question_type in question_types:
            # 1.药病正负相关关系，比如A药可能导致哪些后果？
            # 5.某某药品可能导致哪些不良反应，比如A药可能导致哪些后果？它和问题1的区别只能在查询时进行筛选
            if question_type == 'medicine_symptom':
                keys, values = self.med_symptom(entity_dict)
            # 2.药药之间是否存在相互作用
            elif question_type == 'med_med_relation':
                keys, values = self.med_med_rel(entity_dict)
            # 6.药物禁忌
            elif question_type == 'medicine_taboo':
                keys, values = self.med_taboo(entity_dict)
            # 3.A药品和B药品合用会产生哪些后果
            elif question_type == 'med_med_symptom':
                keys, values = self.med_med_symptom(entity_dict)
            # 4.A药和B药一起服用的临床指导建议
            elif question_type == 'med_med_clinic':
                keys, values = self.med_med_clinic(entity_dict)
            elif question_type == "symptom_cause":
                keys, values = self.symptom_cause(entity_dict)
            elif question_type == "disease_cure":
                keys, values = self.disease_cure(entity_dict)
            else:
                raise NotImplementedError

            if any(values):
                answers.append(self.build_answer(keys, values))
        return answers
    
    

    def med_symptom(self, entities):
        if not entities:
            return []

        # 查询语句
        answers = []
        # 1.药病正负相关关系，比如A药可能导致哪些后果？

        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药病相互作用 relations
        valid_nodes = []
        for node in relevant_node:
            valid_nodes += self.searcher.get_valid_start_node(node, ["包含实体1", "包含实体2"], node_type=["药病相互作用"])
        # get values
        value_nodes = []
        disease_nodes = []
        for node in valid_nodes:
            value_nodes += [r.end_node for r in self.searcher.match_rel(node1=node, rel_type="有无药病正负相关")]
            disease_nodes += [r.end_node for r in self.searcher.match_rel(node1=node, rel_type="包含实体2")]
        # GET ANSWERS
        for i in range(len(disease_nodes)):
            if disease_nodes[i]["name"] == "实验室检查":
                # answers.append(value_nodes[i]["原文信息"])
                pass
            elif value_nodes[i]["作用取值"] == "正相关":
                answers.append(disease_nodes[i]["name"])
        
        # print("rels:", [r.start_node.labels for r in interaction])

        # 不良反应
        potential_answers = []
        reaction_nodes = []
        for node in relevant_node:
            reaction_nodes += self.searcher.get_valid_start_node(node, rel_type="来自药品", node_type=["不良反应"])
        
        for n in reaction_nodes:
            if n["不良反应症状"]:
                potential_answers.append(n["不良反应症状"])
            else:
                potential_answers.append(handle(n["原文信息"]))
        
        return ["高危", "可能"], [answers, potential_answers]
        # ans = self.build_answer(["高危", "可能"], [answers, potential_answers])
        # print(ans)
        # return answers
    
    def med_med_rel(self, entities):
        answers = []
        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药病相互作用 relations
        valid_nodes = []
        for node in relevant_node:
            valid_nodes += self.searcher.get_valid_start_node(node, ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        # get values
        value_nodes = []
        disease_nodes = []
        for node in valid_nodes:
            value_nodes += self.searcher.get_valid_end_node(node, rel_type="有无相互作用存在")

            disease_nodes += self.searcher.get_valid_end_node(node, rel_type=["包含实体2"])

        # GET ANSWERS
        for i in range(len(disease_nodes)):
            if value_nodes[i]["作用取值"] == "有相互作用":
                answers.append(disease_nodes[i]["name"].strip())
                #  + ":" + value_nodes[i]["原文信息"])
        answers = list(set(entities.keys()).difference(set(answers)))
        return ["与以下药物存在相互作用"], [answers]
        # ans = self.build_answer(["与以下药物存在相互作用"], [answers])
        # print(ans)
        # return ans
    
    def build_answer(self, keys, values, default="无相关信息"):
        assert len(keys) == len(values)
        if not any(values):
            ans = default
            return ans
        ans = ""
        for i in range(len(keys)):
            ans += f"[{keys[i]}]\n"
            ans += "\n".join([f"{i+1}. " + handle(a) for i, a in enumerate(values[i])]) + "\n"
        return ans

    
    def med_taboo(self, entities):
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        reaction_nodes = []
        for node in relevant_node:
            reaction_nodes += self.searcher.get_valid_start_node(node, rel_type="来自药品", node_type=["禁忌"])
        
        potential_answers = []
        for n in reaction_nodes:
            people = self.searcher.get_valid_end_node(n, rel_type="禁忌人群")
            if people:
                potential_answers.append(people[0]["name"])

            # potential_answers = [n["原文信息"] for n in reaction_nodes]
            else:
                potential_answers.append(handle(n["原文信息"]))

        
        return ["禁忌"], [potential_answers]
        # ans = self.build_answer(["禁忌"], [potential_answers])
        # print(ans)
        # return ans
    
    def med_med_symptom(self, entities):
        assert len(entities) == 2, print("med_med_symptom must have exactly 2 entities")
        answers = []
        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药病相互作用 relations
        valid_nodes1 = self.searcher.get_valid_start_node(relevant_node[0], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        valid_nodes2 = self.searcher.get_valid_start_node(relevant_node[1], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])

        valid_nodes = list(set(valid_nodes1).intersection(set(valid_nodes2)))
        # get values
        value_nodes = []
        outcome_nodes = []
        for node in valid_nodes:
            outcome = self.searcher.get_valid_end_node(node, rel_type=["有作用结果"])
            if outcome:
                value_nodes += self.searcher.get_valid_end_node(node, rel_type="有无相互作用存在")
                outcome_nodes += outcome


        # GET ANSWERS
        for i in range(len(value_nodes)):
            if value_nodes[i]["作用取值"] == "有相互作用":
                answers.append(outcome_nodes[i]["作用取值"])

        return ["相互作用结果"], [answers]
        # ans = self.build_answer(["相互作用结果"], [answers])
        # print(ans)
        # return ans

    def med_med_clinic(self, entities):
        assert len(entities) == 2, print("med_med_clinic must have exactly 2 entities")
        answers = []
        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药病相互作用 relations
        valid_nodes1 = self.searcher.get_valid_start_node(relevant_node[0], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        valid_nodes2 = self.searcher.get_valid_start_node(relevant_node[1], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])

        valid_nodes = list(set(valid_nodes1).intersection(set(valid_nodes2)))
        # get values
        value_nodes = []
        for node in valid_nodes:
            value_nodes += self.searcher.get_valid_end_node(node, rel_type="有临床指导")

        # GET ANSWERS

        for i in range(len(value_nodes)):
            answers.append(value_nodes[i]["作用取值"])

        return ["临床建议"], [answers]
        # ans = self.build_answer(["临床建议"], [answers])
        # print(ans)
        # return ans
    
    def symptom_cause(self, entities):
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        
        reaction_node = []
        for node in relevant_node:
            reaction_node += self.searcher.get_valid_start_node(node, rel_type=["涉及疾病", "不良反应症状"], node_type=["不良反应"])
        med_nodes = []
        for node in reaction_node:
            med_nodes += self.searcher.get_valid_end_node(node, rel_type="来自药品")
        
        answer = [n["name"] for n in med_nodes]
        return ["可能导致该症状的药物"], [answer]
        # ans = self.build_answer(["可能导致该症状的药物"], [answer])
        # print(ans)
        # return ans
    
    def disease_cure(self, entities):
        answers =[]
        query_for_node = ["MATCH (m) where m.`rdf:subject` = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        cure_nodes = []
        for node in relevant_node:
            cure_nodes += self.searcher.get_valid_start_node(node, rel_type="有描述知识", node_type=["疾病相关治疗"])
        cure_methods = []
        for node in cure_nodes:
            cure_methods += self.searcher.get_valid_end_node(node, rel_type="指南原文信息")
        
        answers = [n["原文信息"] for n in cure_methods]
        return ["治疗方案"], [answers]

if __name__ == '__main__':
    
    
    system = QASystem()
    # ans = system.process("心肌梗死有哪些治疗方案")
    ans = system.process("不良反应心动过速可能是因为什么药品引起的")
    print(ans)
    # system.process("福辛普利钠胶囊和利尿剂一起服用的临床指导建议是什么")
    # system.process("吲达帕胺胶囊和盐酸普萘洛尔缓释胶囊合用会产生什么后果")
    # system.process("吲达帕胺胶囊禁忌")

    # system.process("盐酸普萘洛尔缓释胶囊禁忌")
    # system.process("吲达帕胺胶囊与哪些药物有相互作用")
    # system.process("缬沙坦氢氯噻嗪片有什么副作用")
    # handler = QuestionParser()

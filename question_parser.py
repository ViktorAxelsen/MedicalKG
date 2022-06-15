from answer_search import AnswerSearcher
from visualization import visualize_graph

def handle(text):
    for i in "01234567890.、，。,":
        text = text.strip(i)
    return text.strip()

class QuestionParser:
    def __init__(self):
        self.searcher = AnswerSearcher()
    
    def init_visualize_assets(self):
        self.src = []
        self.dst = []
        self.rels = {}

    def parser_main(self, res_classify):
        entity_dict = res_classify['args']
        question_types = res_classify['question_types']
        answers = []
        for question_type in question_types:
            self.init_visualize_assets()
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
            self.visualize()
        return answers
    
    def update_vis_assets(self, assets):
        self.src += assets[0]
        self.dst += assets[1]
        self.rels.update(assets[2])

    
    def visualize(self):
        return visualize_graph(self.src, self.dst, self.rels)
    

    def med_symptom(self, entities):
        '''
        description: 
            search for symptom and impact of specific medicine
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        # assets for visualization
        src = []
        dst = []
        rels = []

        if not entities:
            return []

        answers = []
        # 1.药病正负相关关系，比如A药可能导致哪些后果？

        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        

        # find 药病相互作用 relations
        valid_nodes = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, ["包含实体1", "包含实体2"], node_type=["药病相互作用"])
            valid_nodes += tmp
            self.update_vis_assets(assets)


        # get related values
        value_nodes = []
        disease_nodes = []
        for node in valid_nodes:
            tmp1, assets = self.searcher.get_valid_end_node(node, rel_type="有无药病正负相关")
            value_nodes += tmp1
            self.update_vis_assets(assets)
            tmp2, assets = self.searcher.get_valid_end_node(node, rel_type="包含实体2")
            disease_nodes += tmp2
            self.update_vis_assets(assets)


            # update visualization ####################
            src += [node["name"]] * len(tmp1)
            dst += [n["name"] for n in tmp1]
            rels += ["有无药病正负相关"] * len(tmp1)
            src += [node["name"]] * len(tmp2)
            dst += [n["name"] for n in tmp2]
            rels += ["包含实体2"] * len(tmp2)
            ###########################################

        # GET ANSWERS
        for i in range(len(disease_nodes)):
            if disease_nodes[i]["name"] == "实验室检查":
                # answers.append(value_nodes[i]["原文信息"])
                pass
            elif value_nodes[i]["作用取值"] == "正相关":
                answers.append(disease_nodes[i]["name"])
        

        # 2. 药物可能导致的不良反应 #######################################################
        potential_answers = []
        reaction_nodes = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, rel_type="来自药品", node_type=["不良反应"])
            reaction_nodes += tmp
            self.update_vis_assets(assets)

        
        for n in reaction_nodes:
            if n["不良反应症状"]:
                potential_answers.append(n["不良反应症状"])
            else:
                potential_answers.append(handle(n["原文信息"]))
        
        return ["高危不良反应", "可能不良反应"], [answers, potential_answers]

    
    def med_med_rel(self, entities):
        '''
        description: 
            search for interaction with other medicines of specific medicine
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        answers = []
        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药药相互作用 relations
        valid_nodes = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
            valid_nodes += tmp
            self.update_vis_assets(assets)

        # get values
        value_nodes = []
        disease_nodes = []
        for node in valid_nodes:
            tmp, assets = self.searcher.get_valid_end_node(node, rel_type="有无相互作用存在")
            value_nodes += tmp
            self.update_vis_assets(assets)

            tmp, assets = self.searcher.get_valid_end_node(node, rel_type=["包含实体2"])
            disease_nodes += tmp
            self.update_vis_assets(assets)

        # GET ANSWERS
        for i in range(len(disease_nodes)):
            if value_nodes[i]["作用取值"] == "有相互作用":
                answers.append(disease_nodes[i]["name"].strip())
                #  + ":" + value_nodes[i]["原文信息"])
        answers = list(set(entities.keys()).difference(set(answers)))
        return ["与以下药物存在相互作用"], [answers]

    
    def build_answer(self, keys, values, default="无相关信息"):
        '''
        description: 
            convert answer_keys and answer_str to string
        args:
            keys: List[str]
            values: List[List[str]]
            default: when any value is empty, return default
        return:
            ans: str
        '''
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
        '''
        description: 
            search for taboo of specific medicine
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        # get main node        
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        
        # get 禁忌 node
        reaction_nodes = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, rel_type="来自药品", node_type=["禁忌"])
            reaction_nodes += tmp
            self.update_vis_assets(assets)
        
        # get 禁忌人群 or 原文信息
        potential_answers = []
        for n in reaction_nodes:
            people, assets = self.searcher.get_valid_end_node(n, rel_type="禁忌人群")
            if people:
                self.update_vis_assets(assets)
                potential_answers.append(people[0]["name"])

            else:
                potential_answers.append(handle(n["原文信息"]))

        
        return ["禁忌"], [potential_answers]

    
    def med_med_symptom(self, entities):
        '''
        description: 
            search for interaction result of two medicines
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        try:
            assert len(entities) == 2
        except:
            print("med_med_symptom must have exactly 2 entities")
            return []
        answers = []
        # find main node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药药相互作用 relations
        valid_nodes1, assets1 = self.searcher.get_valid_start_node(relevant_node[0], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        valid_nodes2, assets2 = self.searcher.get_valid_start_node(relevant_node[1], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        self.update_vis_assets(assets1)
        self.update_vis_assets(assets2)

        # 去重
        valid_nodes = list(set(valid_nodes1).intersection(set(valid_nodes2)))

        # get values
        value_nodes = []
        outcome_nodes = []
        for node in valid_nodes:
            outcome, assets = self.searcher.get_valid_end_node(node, rel_type=["有作用结果"])
            if outcome:
                self.update_vis_assets(assets)
                tmp, assets = self.searcher.get_valid_end_node(node, rel_type="有无相互作用存在")
                value_nodes += tmp
                outcome_nodes += outcome
                self.update_vis_assets(assets)


        # GET ANSWERS
        for i in range(len(value_nodes)):
            if value_nodes[i]["作用取值"] == "有相互作用":
                answers.append(outcome_nodes[i]["作用取值"])

        return ["相互作用结果"], [answers]


    def med_med_clinic(self, entities):
        '''
        description: 
            search for clinical advice for taking two medicines at the same time
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        try:
            assert len(entities) == 2
        except:
            print("med_med_clinic must have exactly 2 entities")
            return []

        answers = []
        # find medical node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)

        # find 药药相互作用 relations
        valid_nodes1, assets1 = self.searcher.get_valid_start_node(relevant_node[0], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        valid_nodes2, assets2 = self.searcher.get_valid_start_node(relevant_node[1], ["包含实体1", "包含实体2"], node_type=["药药相互作用"])
        self.update_vis_assets(assets1)
        self.update_vis_assets(assets2)

        # 去重
        valid_nodes = list(set(valid_nodes1).intersection(set(valid_nodes2)))
        # get values
        value_nodes = []
        for node in valid_nodes:
            tmp, assets = self.searcher.get_valid_end_node(node, rel_type="有临床指导")
            value_nodes += tmp
            self.update_vis_assets(assets)

        # GET ANSWERS
        for i in range(len(value_nodes)):
            answers.append(value_nodes[i]["作用取值"])

        return ["临床建议"], [answers]

    
    def symptom_cause(self, entities):
        '''
        description: 
            search for symptom cause (usually return medicines)
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        # get main node
        query_for_node = ["MATCH (m) where m.name = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        
        # get reaction node
        reaction_node = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, rel_type=["涉及疾病", "不良反应症状"], node_type=["不良反应"])
            reaction_node += tmp
            self.update_vis_assets(assets)
        # get medicine linking to reaction node
        med_nodes = []
        for node in reaction_node:
            tmp, assets = self.searcher.get_valid_end_node(node, rel_type="来自药品")
            med_nodes += tmp
            self.update_vis_assets(assets)
        
        answer = [n["name"] for n in med_nodes]
        return ["可能导致该症状的药物"], [answer]

    
    def disease_cure(self, entities):
        '''
        description: 
            search for cure of a disease
        args:
            entities: a dict containing entity names and corresponding attributes, only name is used here
        return:
            answer_key: List[str]
            answer_str: List[List[str]]
        '''
        answers =[]
        # get main node
        query_for_node = ["MATCH (m) where m.`rdf:subject` = '{0}' return m".format(i) for i in entities]
        relevant_node = self.searcher.search_main(query_for_node)
        # get cure node
        cure_nodes = []
        for node in relevant_node:
            tmp, assets = self.searcher.get_valid_start_node(node, rel_type="有描述知识", node_type=["疾病相关治疗"])
            cure_nodes += tmp
            self.update_vis_assets(assets)
        # get cure methods node
        cure_methods = []
        for node in cure_nodes:
            tmp, assets = self.searcher.get_valid_end_node(node, rel_type="指南原文信息")
            cure_methods += tmp
            self.update_vis_assets(assets)
        
        answers = [n["原文信息"] for n in cure_methods]
        return ["治疗方案"], [answers]

from question_classifier import QuestionClassifier
class QASystem:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
    
    def process(self, question):
        res = self.classifier.classify(question)
        if not res:
            ans = "无法回答"
        else:
            answers = self.parser.parser_main(res)
            ans = "\n".join(answers)
        if not ans:
            ans = "无法回答"
        return ans

if __name__ == '__main__':
    
    system = QASystem()
    for q in ["不良反应心动过速可能是因为什么药品引起的", "福辛普利钠胶囊和利尿剂一起服用的临床指导建议是什么", "吲达帕胺胶囊和盐酸普萘洛尔缓释胶囊合用会产生什么后果", "服用吲达帕胺胶囊有什么禁忌", "吲达帕胺胶囊与哪些药品有相互作用", "缬沙坦氢氯噻嗪片有什么副作用"]:
    # for q in ["富马酸比索洛尔片有什么禁忌?"]:
        print("输入:", q)
        # ans = system.process("心肌梗死有哪些治疗方案")
        print("输出:")
        ans = system.process(q)
        print(ans)
    # system.process("福辛普利钠胶囊和利尿剂一起服用的临床指导建议是什么")
    # system.process("吲达帕胺胶囊和盐酸普萘洛尔缓释胶囊合用会产生什么后果")
    # system.process("吲达帕胺胶囊禁忌")

    # system.process("盐酸普萘洛尔缓释胶囊禁忌")
    # system.process("吲达帕胺胶囊与哪些药物有相互作用")
    # system.process("缬沙坦氢氯噻嗪片有什么副作用")
    # handler = QuestionParser()

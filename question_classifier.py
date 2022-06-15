#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

import os
import ahocorasick

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 加载预训练模型

        #　特征词路径
        self.medicine_path=os.path.join(cur_dir,"./data/medicine.txt")
        self.medicine2_path=os.path.join(cur_dir,"./data/medicine2.txt")
        self.element_path=os.path.join(cur_dir,"./data/element.txt")
        self.abnormal_path=os.path.join(cur_dir,"./data/abnormal.txt")
        self.illness_path=os.path.join(cur_dir,"./data/illness.txt")
        # 加载特征词
        self.medicine_wds=[i.strip() for i in open(self.medicine_path) if i.strip()]
        self.medicine2_wds=[i.strip() for i in open(self.medicine2_path) if i.strip()]
        self.element_wds=[i.strip() for i in open(self.element_path) if i.strip()]
        self.abnormal_wds=[i.strip() for i in open(self.abnormal_path) if i.strip()]
        self.illness_wds=[i.strip() for i in open(self.illness_path) if i.strip()]
        
        self.region_words = set(self.medicine_wds+self.medicine2_wds+self.element_wds+self.abnormal_wds+self.illness_wds)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        # 副作用疑问词,可以是药病相互作用，可以是单个药品可能导致的不良反应
        self.medicine_symptom_qwds = ["影响","副作用","后果","引起","症状","相互","不良反应","导致","问题"]
        # 药药相互作用疑问词，药药冲突
        self.med_med_relation_qwds=["服用","冲突","哪些药","产生影响","合用","一起"]
        # 临床指导建议
        self.clinic_qwds=["临床","如何服用","使用建议","建议"]
        # 药品禁忌疑问词
        self.taboo_qwds=["禁忌","注意","禁忌人群","不能吃","能吃吗"]
        # 疾病的治疗方案
        self.disease_cure_qwds=["治疗","诊疗","方案","怎么治"]

        # print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_
        question_type = 'others'

        question_types = []

        meds=["medicine","medicine2","element"]
        single_med=0
        for i in data["args"].values():
            if i[0] in meds:
                single_med+=1

        # 接下来按问句包括的关键词，对问题的类型进行分类
        # 一、单药品类
        if single_med==1:
            # 1.误用某某药品可能会导致哪些问题？
            # 2.某某药品可能导致哪些不良反应？
            if self.check_words(self.medicine_symptom_qwds,question):
                question_type="medicine_symptom"
                question_types.append(question_type)
            # 3.某某药品有哪些禁忌人群？某某药品有哪些禁忌？
            if self.check_words(self.taboo_qwds,question):
                question_type="medicine_taboo"
                question_types.append(question_type)
            # 4.某某药品和哪些药品有相互作用？
            if self.check_words(self.med_med_relation_qwds,question):
                question_type="med_med_relation"
                question_types.append(question_type)
        # 二、双药品类
        if single_med!=1:
            # 5.A药品和B药品合用会产生哪些后果？
            if self.check_words(self.med_med_relation_qwds,question):
                question_type="med_med_symptom"
                question_types.append(question_type)
            # 6.A药品和B药品一起服用的临床指导建议是什么？
            if self.check_words(self.clinic_qwds,question):
                question_type="med_med_clinic"
                question_types.append(question_type)
        # 三、疾病类
        # 7.不良反应XXX可能是因为什么药品引起的？
        if self.check_words(self.medicine_symptom_qwds,question) and ("abnormal" in types):
            question_type="symptom_cause"
            question_types.append(question_type)
        # 8.XX疾病有哪些治疗方案？
        if self.check_words(self.disease_cure_qwds,question):
            question_type="disease_cure"
            question_types.append(question_type)


        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造关键词对应的类型，像是构建一个关键词到具体类型的映射'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.medicine_wds:
                wd_dict[wd].append('medicine')
            if wd in self.medicine2_wds:
                wd_dict[wd].append("medicine2")
            if wd in self.element_wds:
                wd_dict[wd].append("element")
            if wd in self.abnormal_wds:
                wd_dict[wd].append("abnormal") 
            if wd in self.illness_wds:
                wd_dict[wd].append("illness")   
        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''问句过滤'''
    def check_medical(self, question):
        # 它返回的是这个问句里包含了多少个实体词，比如我只设置了药品这一类，
        # 那么这个结果的长度就是问题里包含的药品数量
        # 如果要问“不良反应XXX可能是因为什么药品引起的”，这就相当于处理返回结果为0的那种情况就行
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        # 最后得到的是[{关键词1：对应的问题类型1},{关键词2：对应的问题类型2},...]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        print(f"question={question}")
        data = handler.classify(question)
        print(data)
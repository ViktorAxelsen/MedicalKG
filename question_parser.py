class QuestionPaser:

    '''解析主函数'''
    def parser_main(self, res_classify):
        entity_dict = res_classify['args']
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            # 1.药病正负相关关系，比如A药可能导致哪些后果？
            # 5.某某药品可能导致哪些不良反应，比如A药可能导致哪些后果？它和问题1的区别只能在查询时进行筛选
            if question_type == 'medicine_symptom':
                sql = self.sql_transfer(question_type, entity_dict)
            # 2.药药之间是否存在相互作用
            elif question_type == 'med_med_relation':
                sql = self.sql_transfer(question_type, entity_dict)
            # 6.药物禁忌
            elif question_type == 'medicine_taboo':
                sql = self.sql_transfer(question_type, entity_dict)
            # 3.A药品和B药品合用会产生哪些后果
            elif question_type == 'med_med_symptom':
                sql = self.sql_transfer(question_type, entity_dict)
            # 4.A药和B药一起服用的临床指导建议
            elif question_type == 'med_med_clinic':
                sql = self.sql_transfer(question_type, entity_dict)

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        if question_type == 'medicine_symptom':
            # 1.药病正负相关关系，比如A药可能导致哪些后果？
            relevant = ["MATCH (m) where m.`包含实体1` = '{0}' and m.type = '药病相互作用' return m.`有无药病正负相关`".format(i) for i in
                        entities]
            if relevant:
                sql = ["MATCH (m:`{0}`) return m.`原文信息`".format(i) for i in relevant]
                sql.append('question_type_1')
            else:
                # 5.某某药品可能导致哪些不良反应，比如A药可能导致哪些后果？,不限制type，因为存在type不等于不良反应的例外
                sql = ["MATCH (m) where m.`来自药品` = '{0}' return m.`原文信息`".format(i) for i in entities]
                sql.append('question_type_5')

        # 2.药药之间是否存在相互作用
        elif question_type == 'med_med_relation':
            relevant = ["MATCH (m) where m.`包含实体1` = `{0}` and m.type = `药药相互作用` return m.`有无相互作用存在`".format(i) for i in entities]
            sql = ["MATCH (m:`{0}`) return m.`原文信息`".format(i) for i in relevant]

        # 6.药物禁忌
        elif question_type == 'medicine_taboo':
            sql = ["MATCH (m) where m.`来自药品` = '{0}' and m.type = '禁忌' return m.`原文信息`".format(i) for i in entities]

        # 3.A药品和B药品合用会产生哪些后果
        elif question_type == 'med_med_symptom':
            sql = ["MATCH (m) where m.type = '药药相互作用' and m.`包含实体1` = `{0}` and m.`包含实体2` = `{1}` return m.'说明书原文信息'".format(i, j) for i, j in entities]
            if not sql:
                sql = ["MATCH (m) where m.type = '药药相互作用' and m.`包含实体1` = `{1}` and m.`包含实体2` = `{0}` return m.'说明书原文信息'".format(i, j) for i, j in entities]

        # 4.A药和B药一起服用的临床指导建议
        elif question_type == 'med_med_clinic':
            clinical = ["MATCH (m) where m.type = '药药相互作用' and m.`包含实体1` = `{0}` and m.`包含实体2` = `{1}` return m.'有临床指导'".format(i, j) for i, j in entities]
            if not clinical:
                clinical = ["MATCH (m) where m.type = '药药相互作用' and m.`包含实体1` = `{1}` and m.`包含实体2` = `{0}` return m.'有临床指导'".format(i, j) for i, j in entities]
            sql = ["MATCH (m:`{0}`) return m.`原文信息`".format(i) for i in clinical]

        return sql


if __name__ == '__main__':
    handler = QuestionPaser()

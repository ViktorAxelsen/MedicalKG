from question_classifier import *
from question_parser import *
from answer_search import *
import random


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
    
    def chat_main(self, question):
        answer = '不好意思，未查询到相关结果，请尝试换一种提问方式'
        res = self.classifier.classify(question)
        if not res:
            return answer
        else:
            answers = self.parser.parser_main(res)
            if not answers:
                return answer
            ans = "\n".join(answers)
        return ans


def QA():
    questions = ["不良反应心动过速可能是因为什么药品引起的", "福辛普利钠胶囊和利尿剂一起服用的临床指导建议是什么", "西尼地平片和伊曲康唑合用会产生什么后果", "服用吲达帕胺胶囊有什么禁忌", "吲达帕胺胶囊与哪些药品有相互作用", "缬沙坦氢氯噻嗪片有什么副作用"]
    print("高血压问答小助手已启动……")
    print("*"*30)
    print("你可以这么问我: \n%s" %("\n".join(questions)))
    print("*"*30)
    handler = ChatBotGraph()
    while 1:
        question = input('请输入你的问题或敲击[回车]随机生成一个问题:')
        if not question.strip():
            question = random.choice(questions)
            print("问题:", question)
        answer = handler.chat_main(question)
        print('回答:', answer)


if __name__ == '__main__':
    QA()
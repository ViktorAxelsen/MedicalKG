from question_classifier import *
from question_parser import *
from answer_search import *


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
            ans = "\n".join(answers)
        return ans


def QA():
    handler = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('Answer:', answer)


if __name__ == '__main__':
    QA()
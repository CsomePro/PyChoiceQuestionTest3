from KVDatabase import KVDatabase
from QuestionBase import *
from QuestionJudge import QuestionJudge
import random
import os

random.seed(os.urandom(8))


class QuestionGenerator:
    def __init__(self, database: KVDatabase, idx_shuffle=True, option_shuffle=True):
        self.database = database
        self.idx_shuffle = idx_shuffle
        self.option_shuffle = option_shuffle
        self.p = 0
        self.index = None

    def make_index(self):
        self.index = self.database.get_index()
        if self.idx_shuffle:
            random.shuffle(self.index)

    def generate(self, judge: QuestionJudge = None):
        if self.index is None:
            self.make_index()
        if self.p >= len(self.index):
            return None
        q: Question = self.database.read(self.index[self.p])
        self.p += 1
        if judge is not None:
            judge.pending(q)
        return self.render(q)

    def render(self, q: Question):
        q = self.make_option(q)
        return q

    def make_option(self, q: Question):
        if self.option_shuffle:
            tmp = list(range(len(q.options)))
            random.shuffle(tmp)

            def f(y):
                return list(map(lambda x: y[x], tmp))

            q.options = f(q.options)
            q.answer = f(q.answer)
        return q


if __name__ == '__main__':
    kvj = KVDatabase.getKVDatabase('question', 'test.json')
    qg = QuestionGenerator(kvj)
    qj = QuestionJudge()
    print(qg.generate(qj))
    qj.judge([1, 0, 1])
    print(qg.generate(qj))
    qj.judge([1, 0, 1])
    print(qg.generate(qj))
    qj.judge([1, 0, 1])
    print(qj.report())

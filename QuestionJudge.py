from QuestionBase import *
import typing


class Report:
    def __init__(self, combo, total, accum):
        self.combo = combo
        self.total = total
        self.accum = accum

    def get_score_proportion(self):
        return int(self.accum / self.total * 10000) / 100

    def __str__(self):
        return 'Report(%r, %r, %r)' % (self.combo, self.total, self.accum)


class QuestionJudge:
    def __init__(self):
        self.pending_question: typing.Optional[Question] = None
        self.combo = 0
        self.total = 0
        self.accum = 0

    def judge(self, answer: list):
        if self.pending_question is None:
            return None
        ans = list(map(lambda x: x[0] == x[1], zip(answer, self.pending_question.answer)))
        if len(answer) != len(self.pending_question.answer):
            ans = [0]
        self.total += self.pending_question.score
        if all(ans):
            self.accum += self.pending_question.score
            self.combo += 1
        else:
            self.combo = 0
        self.pending_question = None
        return ans

    def pending(self, q: Question):
        self.pending_question = q

    def report(self) -> Report:
        return Report(combo=self.combo, total=self.total, accum=self.accum)

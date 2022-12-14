import typing


class QuestionType:
    SINGLE = 1
    MULTIPLE = 2
    JUDGEMENTAL = 3
    UNKNOWN = 0

    # def __init__(self, name, value):
    #     self.name = name
    #     self.value = value
    #
    # def __str__(self):
    #     return self.name
    #
    # def __eq__(self, other):
    #     if not isinstance(other, QuestionType):
    #         return False
    #     return self.value == other.value


# SINGLE = QuestionType("SINGLE", 1)
# MULTIPLE = QuestionType("MULTIPLE", 2)
# JUDGEMENTAL = QuestionType("JUDGEMENTAL", 3)
# UNKNOWN = QuestionType("UNKNOWN", 0)




class Question:
    def __init__(self, problemSurface='', answer=None, options=None, pType=QuestionType.SINGLE):
        if options is None:
            options = []
        if answer is None:
            answer = []
        self.problemSurface: str = problemSurface
        self.answer: typing.List[str] = answer
        self.options: typing.List[int] = options
        self.type: int = pType
        self.score = 1

    def to_tuple(self):
        return self.problemSurface, self.answer, self.options, self.type

    def __str__(self):
        return f"question(%r, %r, %r, %r)" % (self.problemSurface, self.answer, self.options, self.type)

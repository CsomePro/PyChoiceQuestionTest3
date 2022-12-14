from QuestionBase import *
from Util import *
import json
import typing


class KVDatabase:
    def __init__(self, *args, **kwargs):
        pass

    def get_index(self):
        pass

    def read_all(self, limit=-1):
        pass

    def read(self, idx) -> Question:
        pass

    def delete(self, idx) -> int:
        pass

    def update(self, idx, q: Question) -> int:
        pass

    def create(self, q: Question) -> int:
        pass

    def save(self, *args, **kwargs):
        pass

    def load(self, *args, **kwargs):
        pass

    @staticmethod
    def getKVDatabase(mode='None', *args, **kwargs):
        if mode == 'question':
            return KVDatabase_json(*args, **kwargs)


class KVDatabase_json(KVDatabase, ScheduleTask):
    def __init__(self, json_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super(KVDatabase, self).__init__(5)
        self.json_file = json_file
        self.database: typing.Optional[dict] = None
        self.last_idx: int = 0
        self.open_json(json_file)

    def do_check(self):
        print("check")
        self.save()

    def get_index(self):
        return list(self.database.keys())

    def read_all(self, limit=-1):
        mp = map(lambda q: (q[0], Question(*q[1])), self.database.items())
        if limit == -1:
            return list(mp)
        else:
            res = []
            for i, x in zip(range(limit), mp):
                res.append(x)
            return res

    def read(self, idx) -> Question:
        return Question(*self.database[idx])

    def delete(self, idx) -> int:
        del self.database[idx]
        return idx

    def update(self, idx, q: Question) -> int:
        self.database[idx] = q.to_tuple()
        return idx

    def create(self, q: Question) -> int:
        self.last_idx += 1
        self.database[self.last_idx] = q.to_tuple()
        return self.last_idx

    def save(self, *args, **kwargs):
        self.save_json(*args, **kwargs)

    def load(self, *args, **kwargs):
        self.open_json(*args, **kwargs)

    def open_json(self, json_file=None):
        self.json_file = self.json_file if json_file is None else json_file
        with open(self.json_file, "r", encoding='utf-8') as f:
            self.database: dict = {int(k): v for k, v in json.load(f).items()}
        self.last_idx = max({0} | self.database.keys())

    def save_json(self, json_file=None):
        self.json_file = self.json_file if json_file is None else json_file
        with open(self.json_file, "w", encoding='utf-8') as f:
            json.dump(self.database, f)


if __name__ == '__main__':
    kvj = KVDatabase_json("test.json")
    # q1 = Question("1+1=?", [1, 0], ["2", "1"], QuestionType.SINGLE)
    # q2 = Question("1+1<=?", [1, 0, 1], ["2", "1", "3"], QuestionType.MULTIPLE)
    # q3 = Question("1+1=2?", [1, 0], ["yes", "no"], QuestionType.JUDGEMENTAL)
    # ql = [q1, q2, q3]
    # for q in ql:
    #     kvj.create(q)
    # kvj.save_json()
    print(kvj.read(1))
    print(kvj.get_index())

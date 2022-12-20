from QuestionBase import *
from Util import *
import json
import typing


class BankDatabase:
    """
    题库数据库抽象
    switch() 切换题库
        get_bank() 获取题库
    """

    def __init__(self, *args, **kwargs):
        pass

    def switch(self, *args, **kwargs) -> None:
        pass

    def get_bank(self) -> list:
        pass

    def create_bank(self, *args, **kwargs):
        pass


class KVDatabase:
    """
    数据库抽象类
    get_index() 获取index，上层提供idx索引
    read(int) create(Object) update(int, Object) delete(int) 经典CURD操作
    read_all(int) 获取一定数量的数据序列
    save() load() 加载以及保存数据库
    """

    def __init__(self, *args, **kwargs):
        pass

    def get_index(self) -> typing.List:
        pass

    def read_all(self, limit=-1) -> typing.List[typing.Tuple[int, Question]]:
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
            # return KVDatabase_redis(*args, **kwargs)


class KVDatabase_json(KVDatabase, ScheduleTask, BankDatabase):
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

    def switch(self, file=None):
        self.open_json(file)

    def get_bank(self) -> list:
        import os
        dir_bank = '.\\bank'
        return list(
            map(lambda x: os.path.join(dir_bank, x), filter(lambda x: x.endswith('.json'), os.listdir(dir_bank))))

    def create_bank(self, file):
        with open(file, "w") as f:
            f.write("{}")
        self.open_json(file)


class KVDatabase_redis(KVDatabase, ScheduleTask, BankDatabase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super(KVDatabase, self).__init__(10)
        self.redis = self.connect()
        self.last_idx: int = max([0] + self.get_index())

    @staticmethod
    def connect():
        import redis
        import os
        return redis.Redis(host=os.environ.get('REDIS_IP'),
                           port=16379,
                           decode_responses=True,
                           password=os.environ.get('REDIS_PASSWORD'))

    def reconnect(self):
        self.redis.close()
        self.redis = self.connect()

    def do_check(self):
        print("check")
        if not self.redis.ping():
            self.reconnect()

    def get_index(self) -> typing.List:
        return list(map(lambda x: self.key2idx(x), filter(lambda x: x.startswith('Q_'), self.redis.keys())))

    def read_all(self, limit=-1) -> typing.List[typing.Tuple[int, Question]]:
        key = self.get_index()
        return list(map(lambda x: (x, self.str2question(self.redis.get(self.idx2key(x)))), key))

    def read(self, idx) -> Question:
        k = self.idx2key(idx)
        return self.str2question(self.redis.get(k))

    def delete(self, idx) -> int:
        self.redis.delete(self.idx2key(idx))
        return idx

    def update(self, idx, q: Question) -> int:
        self.redis.set(self.idx2key(idx), self.question2str(q))
        return idx

    def create(self, q: Question) -> int:
        self.last_idx += 1
        k = self.idx2key(self.last_idx)
        self.redis.set(k, self.question2str(q))
        return self.last_idx

    def save(self, *args, **kwargs):
        pass

    def load(self, *args, **kwargs):
        pass

    @staticmethod
    def idx2key(idx) -> str:
        return f"Q_{idx:08d}"

    @staticmethod
    def key2idx(s) -> int:
        return int(s[2:])

    @staticmethod
    def question2str(q: Question) -> str:
        return json.dumps(q.to_tuple())

    @staticmethod
    def str2question(s) -> Question:
        surface, ans, options, t = json.loads(s)
        return Question(problemSurface=surface, answer=ans, options=options, pType=t)


if __name__ == '__main__':
    # kvj = KVDatabase_json("bank/test.json")
    # kvj = KVDatabase_redis()
    # q1 = Question("1+1=?", [1, 0], ["2", "1"], QuestionType.SINGLE)
    # q2 = Question("1+1<=?", [1, 0, 1], ["2", "1", "3"], QuestionType.MULTIPLE)
    # q3 = Question("1+1=2?", [1, 0], ["yes", "no"], QuestionType.JUDGEMENTAL)
    # ql = [q1, q2, q3]
    # for q in ql:
    #     kvj.create(q)
    # kvj.save_json()
    # print(kvj.read(3))
    # print(kvj.get_index())
    # print(kvj.get_bank())

    def test(kvj: KVDatabase):
        import time
        s = time.time()
        for i in range(100000):
            kvj.read(1)
        print(time.time() - s)

    test(KVDatabase_json("bank/test.json"))
    test(KVDatabase_redis())


import re
import typing
from typing import Tuple, Any
from ListView import ItemValid


class RExpNode(ItemValid):
    def __init__(self, expObj):
        super().__init__()
        self.exp = expObj
        self.pattern = None
        self.group_id = 0
        self.child_node: [RExpNode] = []
        self.tag = ''

    def get_exp(self):
        return self.exp

    def compile(self):
        try:
            self.pattern = re.compile(self.get_exp())
        except re.error:
            # print(self.get_exp())
            self.pattern = None

    def match(self, target):
        return self.pattern.search(target)

    def parse(self, string, remove=True, ) -> tuple[Any, ...]:
        self.compile()
        mc = self.match(string)
        ans = mc.group(self.group_id)
        res = []
        tmp = string[:mc.span(self.group_id)[0]]
        dt_res = {}
        for ch in self.child_node:
            s, sp, dt = ch.parse(ans)
            res.append(s)
            dt_res.update(dt)
            if remove:
                tmp += ans[:sp[0]]
            else:
                tmp += ans[:sp[1]]
            ans = ans[sp[1]:]
        tmp += ans
        dt_res.update({self.tag: tmp if res else ans})
        return (tmp, tuple(res)) if res else ans, mc.span(self.group_id), dt_res

    def get_groups(self):
        self.compile()
        if self.pattern is not None:
            return self.pattern.groups
        else:
            return None

    def set_group_id(self, idx):
        self.group_id = idx

    def add_child(self, rn):
        self.child_node.append(rn)

    def delete_child(self, idx):
        del self.child_node[idx]

    def check(self):
        self.child_node = self._check(self.child_node)


class RExpNodeValid(RExpNode):
    def get_exp(self):
        return self.exp.get()

    def set_exp(self, s):
        return self.exp.set(s)

    def print(self, prefix=''):
        print(prefix, '->', self.exp.get(), sep='')
        for ct in self.child_node:
            ct.print(prefix + '***')

    def save(self):
        res = []
        for ch in self.child_node:
            res.append(ch.save())
        return self.get_exp(), self.group_id, self.tag, res

    def load(self, x):
        exp, self.group_id, self.tag, res = x
        self.set_exp(exp)
        for ch, rs in zip(self.child_node, res):
            ch.load(rs)


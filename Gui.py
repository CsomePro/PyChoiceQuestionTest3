from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox, simpledialog
import ctypes
import typing
from ListView import *

from QuestionBase import *
from KVDatabase import *
from QuestionJudge import *
from QuestionGenerator import *
from QuestionREPrase import *
from ListView import *

from Util import *


class FrameAll(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


# class Form(FrameAll):
#     def __init__(self, parent, keys: list, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         self.keys = keys

class JudgeFrame(FrameAll):
    def __init__(self, parent, options, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.options = options

    def get_answer(self) -> list:
        pass

    def clean(self):
        pass

    @staticmethod
    def get_judge_frame(p_type, options, parent, *args, **kwargs):
        if p_type == QuestionType.SINGLE or p_type == QuestionType.JUDGEMENTAL:
            return SingleJudge(parent, options, *args, **kwargs)
        elif p_type == QuestionType.MULTIPLE:
            return MultipleJudge(parent, options, *args, **kwargs)


class SingleJudge(JudgeFrame):
    def __init__(self, parent, options, *args, **kwargs):
        super().__init__(parent, options, *args, **kwargs)

        self.ans = IntVar()
        self.radios = [Radiobutton(self, text=_, variable=self.ans, value=i + 1) for i, _ in enumerate(options)]
        ROWMAX = 3
        for i, radio in enumerate(self.radios):
            radio.grid(row=i // ROWMAX + 1, column=i % ROWMAX + 1)

    def get_answer(self):
        ans = [0] * len(self.radios)
        if self.ans.get() > 0:
            ans[self.ans.get() - 1] = 1
        return ans

    def clean(self):
        self.ans.set(0)


class MultipleJudge(JudgeFrame):
    def __init__(self, parent, options, *args, **kwargs):
        super().__init__(parent, options, *args, **kwargs)

        self.ans = [IntVar() for _ in range(len(self.options))]
        self.radios = [Checkbutton(self, text=s, variable=v, onvalue=1, offvalue=0)
                       for i, (s, v) in enumerate(zip(options, self.ans))]
        ROWMAX = 3
        for i, radio in enumerate(self.radios):
            radio.grid(row=i // ROWMAX + 1, column=i % ROWMAX + 1)

    def get_answer(self):
        return list(map(lambda x: x.get(), self.ans))

    def clean(self):
        for ans in self.ans:
            ans.set(0)


class Practice(FrameAll):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.surface = Frame(self)
        self.options = Frame(self)
        self.report = Frame(self)
        self.operate = Frame(self)

        self.surface.place(relx=0, rely=0, relwidth=0.8, relheight=0.8)
        self.options.place(relx=0, rely=0.8, relwidth=0.8, relheight=0.2)
        self.report.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.6)
        self.operate.place(relx=0.8, rely=0.6, relwidth=0.2, relheight=0.4)

        self.startBtn = Button(self.operate, text="开始", command=self.start)
        self.acceptBtn = Button(self.operate, text="确认", command=self.accept)
        self.cleanBtn = Button(self.operate, text="清空", command=self.clean)
        self.nextBtn = Button(self.operate, text="下一题", command=self.next_question)
        self.preBtn = Button(self.operate, text="上一题", command=self.pre_question)
        for btn in [self.startBtn, self.acceptBtn, self.cleanBtn, self.preBtn, self.nextBtn]:
            btn.pack(side=TOP, fill=Y)

        self.combo = StringVar()
        self.accum = StringVar()
        self.rate = StringVar()
        # Label(self.report, textvariable=)
        self.strings = [self.combo, self.accum, self.rate]
        for s in self.strings:
            Label(self.report, textvariable=s).pack(side=TOP, fill=Y)

        self.question_surface = Text(self.surface)
        self.question_surface.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.question_judge: typing.Optional[QuestionJudge] = None
        self.question_generator: typing.Optional[QuestionGenerator] = None
        self.database = global_database
        self.judge: typing.Optional[JudgeFrame] = None

    def make_strings(self, *args):
        for s, string in zip(args, self.strings):
            string.set(str(s))

    def render_options(self, options: list, pType: int):
        if self.judge is not None:
            self.judge.destroy()
        self.judge = JudgeFrame.get_judge_frame(pType, options, self.options)
        self.judge.place(relx=0.5, rely=0.5, relwidth=0.98, relheight=0.98, anchor=CENTER)

    def render_surface(self, surface: str):
        self.question_surface.delete('1.0', END)
        self.question_surface.insert('1.0', surface)

    def render_report(self, rp: Report):
        self.make_strings(rp.combo, rp.accum, rp.get_score_proportion())

    def next_question(self):
        question = self.question_generator.generate(self.question_judge)
        print(question)
        if question is None:
            return
        self.render_options(question.options, question.type)
        self.render_surface(question.problemSurface)

    def pre_question(self):
        pass

    def start(self):
        self.question_judge = QuestionJudge()
        self.question_generator = QuestionGenerator(self.database)
        self.next_question()

    def accept(self):
        if self.judge is None:
            return
        ans = self.judge.get_answer()
        if not any(ans):
            return
        self.question_judge.judge(ans)
        self.next_question()
        self.render_report(self.question_judge.report())

    def clean(self):
        if self.judge is None:
            return
        self.judge.clean()


class RExpTreeView(ItemView):
    def __init__(self, parent, item: RExpNodeValid, *args, **kwargs):
        super().__init__(parent, item, *args, **kwargs)
        self.f1 = Frame(self)
        self.f2 = Frame(self)
        self.f1.pack(side=TOP, anchor=NW)
        self.f2.pack(side=TOP, anchor=NW)
        self.entry = Entry(self.f1, textvariable=item.exp, width=30)
        self.entry.pack(side=LEFT, anchor=NW)
        self.combo = Combobox(self.f1, width=3, values=['0'])
        self.combo.current(0)
        self.combo.pack(side=LEFT, anchor=NW)
        self.combo2 = Combobox(self.f1, width=3, values=['none', 'surface', 'answer',
                                                         'A', 'B', 'C', 'D', 'E', 'F', 'G'])
        self.combo2.current(0)
        self.combo2.pack(side=LEFT, anchor=NW)
        Button(self.f1, text='+', command=self.add_child, width=3).pack(side=LEFT, anchor=NW)
        self.deleteBtn = Button(self.f1, text='-', command=self.delete_self, width=3)
        self.deleteBtn.pack(side=LEFT, anchor=NW)
        self.child: typing.Optional[Widget] = None
        self.item = item
        self.entry.bind('<FocusOut>', self.handle_input)
        self.entry.bind('<KeyRelease>', self.handle_input)
        self.combo.bind('<<ComboboxSelected>>', self.handle_select)
        self.combo2.bind('<<ComboboxSelected>>', self.handle_select_2)
        self.handle_select(None)
        self.handle_select_2(None)

    def reverse_set(self):
        self.handle_input(None)
        self.combo.set(str(self.item.group_id))
        self.combo2.set(self.item.tag)

    def handle_select_2(self, event):
        self.item.tag = self.combo2.get()

    def handle_select(self, event):
        self.item.set_group_id(int(self.combo.get()))

    def handle_input(self, event):
        x = self.item.get_groups()
        if x is None:
            x = 0
        value = list(map(str, range(x + 1)))
        self.combo.config(values=value)
        self.combo.update()

    def add_child(self):
        if self.child is None:
            self.child = TreeListFrame(self.f2, ItemAdapter(RExpTreeView), self.update)
            Label(self.f2, text='--').pack(side=LEFT, anchor=NW)
            self.child.pack(side=LEFT, anchor=NW)
        it = RExpNodeValid(StringVar())
        self.child.insert_item(it)
        self.master.update()
        self.item.add_child(it)

    def delete_self(self):
        self.destroy()
        self.item.valid = False
        self.master.update()

    def update(self) -> None:
        if self.child and not self.child.children:
            print(self, self.child.children)
            while self.f2.children:
                k, v = self.f2.children.popitem()
                v.destroy()
            self.child = None
        self.item.check()
        super(RExpTreeView, self).update()

    # def load(self, x):
    #     _, _, _, res = x
    #     for i in range(res):


class RExpFrame(Frame):
    def __init__(self, parent, RExpRoot: RExpNodeValid, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.scrollbar = Scrollbar(self)
        self.canvas_frame = CanvasFrame(self)
        self.tree_list_frame = TreeListFrame(self.canvas_frame.get_frame(),
                                             ItemAdapter(RExpTreeView), self.canvas_frame.update)
        self.canvas_frame.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas_frame.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas_frame.pack(expand=True, fill=BOTH)
        self.tree_list_frame.pack(expand=True, fill=BOTH)
        self.tree_list_frame.insert_item(RExpRoot)
        self.canvas_frame.update()

    @staticmethod
    def _load(tr, x):
        _, _, _, res = x
        for i in range(len(res)):
            tr.add_child()
        if res:
            for rs, v in zip(res, tr.child.children.values()):
                RExpFrame._load(v, rs)

    @staticmethod
    def _reverse_set(tr):
        tr.reverse_set()
        if tr.child:
            for v in tr.child.children.values():
                RExpFrame._reverse_set(v)

    def load(self, x, flag=0):
        RExpFrame._load(list(self.tree_list_frame.children.values())[0], x)

    def reverse_set(self):
        RExpFrame._reverse_set(list(self.tree_list_frame.children.values())[0])


class OptionsItem(ItemValid):
    def __init__(self):
        super().__init__()
        self.radio = IntVar()
        self.content = StringVar()

    def get(self):
        return self.radio.get(), self.content.get()

    def set(self, x, s):
        self.radio.set(x)
        self.content.set(s)


class OptionItemView(ItemView):
    def __init__(self, parent, item: OptionsItem, *args, **kwargs):
        super().__init__(parent, item, *args, **kwargs)

        self.radio = item.radio
        self.radio.set(0)
        Checkbutton(self, variable=self.radio, onvalue=1, offvalue=0).pack(side=LEFT, anchor=NW)
        self.content = item.content
        Entry(self, textvariable=self.content).pack(side=LEFT, anchor=NW)

        Button(self, text='-', command=self.destroy, width=3).pack(side=LEFT, anchor=NW)
        self.item = item

    def delete(self):
        self.destroy()
        self.item.destroy()
        self.master.update()


class QuestionDetail(simpledialog.Dialog):
    def __init__(self, parent, qid=-1):
        self.songAttr = ["ID", "题面", "正确选项"]
        # self.strings = [StringVar() for _ in range(len(self.songAttr))]
        self.qid = qid
        # self.old_id_list = []
        self.items = []
        super().__init__(parent, "题目详情")

    def body(self, master):
        labels = [Label(master, text=_) for _ in self.songAttr]
        self.id_str = StringVar()
        self.id_view = Entry(master, textvariable=self.id_str)
        self.surface_text = Text(master, height=10)
        self.f0 = Frame(master)
        self.f1 = Frame(self.f0)
        self.options_view = ListView(self.f1, ItemAdapter(OptionItemView), self.check)
        scroll = Scrollbar(self.f1)
        self.options_view.config(yscrollcommand=scroll.set)
        scroll.config(command=self.options_view.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.options_view.pack(expand=True, fill=BOTH)
        Button(self.f0, text="+", width=5, command=self.add_option).pack(side=LEFT, anchor=NW)
        self.f1.pack(expand=True, fill=BOTH)
        entries = [self.id_view, self.surface_text, self.f0]
        for i, (label, entry) in enumerate(zip(labels, entries)):
            label.grid(row=i, column=0, pady=5, sticky='nw')
            entry.grid(row=i, column=1, pady=5, sticky='w')

        # @usingThread(1)
        # def loadSongInfo():
        #     pass
        #
        # loadSongInfo()
        if self.qid != -1:
            self.id_view.config(state='readonly')
            self.id_str.set(str(self.qid))
            self.render_question(global_database.read(self.qid))
        else:
            tmp = Question(problemSurface="题目描述", answer=[0,0,0], options=['选项1','选项2', '选项3'])
            self.render_question(tmp)

        return None

    def add_option(self):
        option = OptionsItem()
        self.items.append(option)
        self.options_view.add_item(option)

    def check(self):
        self.items = ItemValid._check(self.items)

    def render_question(self, q: Question):
        self.surface_text.delete('1.0', END)
        self.surface_text.insert('1.0', q.problemSurface)
        self.options_view.clean()
        tmp = list(zip(q.answer, q.options))
        self.items = [OptionsItem() for _ in range(len(tmp))]
        for t, it in zip(tmp, self.items):
            self.options_view.add_item(it)
            it.set(*t)

    def apply(self):
        if not self.id_str.get() or int(self.id_str.get()) < 0:
            return
        self.check()
        tmp = list(filter(lambda x: 0 <= x[0] <= 1 and x[1].strip(), map(lambda x: x.get(), self.items)))
        answer, options = zip(*tmp)
        print(answer, options)
        q = Question(problemSurface=self.surface_text.get('1.0', END), answer=answer, options=options,
                 pType=QuestionType.SINGLE if sum(answer) == 1 else QuestionType.MULTIPLE)
        global_database.update(int(self.id_str.get()), q)
        showinfo("提示", f"成功")

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="确认", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="取消", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        # self.initial_focus = w

        box.pack()


class QuestionManageFrame(FrameAll):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        attrLength = [120, 20, 200]
        attr = ["题面", "正确答案", "选项"]
        self.sid = 0
        self.submit_id = 0
        self.myTreeFrame = Frame(self)
        self.myScrollbarV = Scrollbar(self.myTreeFrame)
        self.myScrollbarH = Scrollbar(self.myTreeFrame, orient=HORIZONTAL)
        self.myTreeView = Treeview(self.myTreeFrame, columns=attr)
        for songTmp, attrLength in zip(attr, attrLength):
            self.myTreeView.column(songTmp, width=attrLength)
            self.myTreeView.heading(songTmp, text=songTmp)
        self.myTreeView.column("#0", width=10)
        self.myTreeView.heading("#0", text="ID")
        self.myMenu = Menu(self, tearoff=False)
        self.myTreeView.bind("<3>", lambda e: self.myMenu.post(e.x_root, e.y_root))
        self.myTreeView.bind('<<TreeviewSelect>>', self.treeViewSelect)
        self.myTreeView.bind('<Double-Button-1>', self.detail)
        self.myMenu.add_command(label='刷新', command=self.refresh)
        self.myMenu.add_command(label='添加', command=self.add_question)
        self.myMenu.add_command(label='编辑', command=self.detail)
        self.drawFrame()
        self.refresh()

    def drawFrame(self):
        self.myTreeFrame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor=CENTER)
        self.myScrollbarV.pack(side=RIGHT, fill=Y)
        self.myScrollbarH.pack(side=BOTTOM, fill=X)
        self.myTreeView.pack(expand=True, fill=BOTH)
        self.myScrollbarV.config(command=self.myTreeView.yview)
        self.myScrollbarH.config(command=self.myTreeView.xview)
        self.myTreeView.config(yscrollcommand=self.myScrollbarV.set,
                               xscrollcommand=self.myScrollbarH.set)

    @staticmethod
    def render_question(q: Question):
        key = 'ABCDEFGH'
        return q.problemSurface, \
               ''.join(map(lambda x: key[x[0]] if x[1] else "", enumerate(q.answer))), \
               ' '.join(map(lambda x: f"{key[x[0]]}{x[1]}", enumerate(q.options)))

    @usingThread(1)
    def refresh(self):
        self.myTreeView.delete(*self.myTreeView.get_children())
        for i, data in enumerate(global_database.read_all()):
            idx, q = data
            self.myTreeView.insert('', i, text=str(idx), values=self.render_question(q))

    def treeViewSelect(self, event):
        # self.sid = int(self.myTreeView.set(self.myTreeView.selection())['歌曲id'])
        # self.submit_id = int(event.widget.item(event.widget.selection())['text'])
        # self.sid = int()
        tmp = event.widget.item(event.widget.selection())['text']
        if tmp:
            self.sid = int(tmp)

    def add_question(self):
        QuestionDetail(self)
        self.refresh()

    def detail(self, *args, **kwargs):
        QuestionDetail(self, self.sid)
        self.refresh()


class RExpParse(FrameAll):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.re_root = RExpNodeValid(StringVar())

        self.text = Text(self)
        self.re_frame = RExpFrame(self, self.re_root)
        self.operate_frame = Frame(self)
        list(self.re_frame.tree_list_frame.children.values())[0].deleteBtn.destroy()

        self.text.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.re_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.7)
        self.operate_frame.place(relx=0.5, rely=0.7, relwidth=0.5, relheight=0.3)

        Button(self.operate_frame, text="保存", command=self.save).pack()
        Button(self.operate_frame, text="加载", command=self.load).pack()
        Button(self.operate_frame, text="识别", command=self.parse).pack()

        self.load()

    def parse(self):
        data = self.text.get('1.0', END)
        _, sp, dt = self.re_root.parse(data)
        print(sp)
        print(dt)
        key = 'ABCDEFGH'
        key = {_: i for i, _ in enumerate(key)}
        max_ans = 0
        for k, v in key.items():
            if dt.get(k, None) is not None:
                max_ans = max(max_ans, v + 1)
        answer = [0] * max_ans
        for k in dt['answer']:
            answer[key[k]] = 1

        options = []
        for k in "ABCDEFGH":
            if k in dt:
                options.append(dt[k])

        q = Question(problemSurface=dt['surface'], answer=answer, options=options, pType=QuestionType.SINGLE)
        print(q)
        global_database.create(q)

        data = data[sp[1]:]
        self.text.delete("1.0", END)
        self.text.insert('1.0', data)

    def save(self):
        s = json.dumps(self.re_root.save())
        with open("user.json", "w") as f:
            f.write(s)
        global_database.save_json()

    def load(self):
        with open("user.json", "r") as f:
            data = json.load(f)
        # print(data)
        self.re_frame.load(data, 0)
        self.re_root.load(data)
        self.re_frame.reverse_set()


class Gui:
    def __init__(self):
        self.srcPATH = ''
        self.savePATH = ''

        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        try:
            from ttkbootstrap import Style
            style = Style(theme='cosmo')
            self.root = style.master
        except ImportError:
            self.root = Tk()
        # self.root = style.master
        self.root.title('CodeCompressor by CSOME')
        self.root.geometry('800x600+100+100')
        self.root.tk.call('tk', 'scaling', ScaleFactor / 75)

        self.notebook = Notebook(self.root)
        self.notebook.place(relx=0, rely=0, relwidth=1, relheight=1)
        for k, v in self.make_frame().items():
            v.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.notebook.add(v, text=k)

    def make_frame(self) -> dict:
        self.practice = Practice(self.root)
        self.prase = RExpParse(self.root)
        self.manager = QuestionManageFrame(self.root)
        return {
            "练习": self.practice,
            "管理": self.manager,
            "识别": self.prase,
        }

    def main(self):
        self.root.mainloop()


if __name__ == '__main__':
    global_database = KVDatabase.getKVDatabase("question", "test.json")
    sc = Schedule([global_database])
    a = Gui()
    sc.start()
    a.main()
    sc.stop()
    print(1)

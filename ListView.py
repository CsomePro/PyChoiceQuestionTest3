import typing
from tkinter import *
from tkinter.ttk import *


class Item:
    def __init__(self):
        pass


class ItemValid(Item):
    def __init__(self):
        super().__init__()
        self.valid = True

    @staticmethod
    def _check(child):
        return list(filter(lambda x: x.valid, child))

    def check(self):
        pass

    def destroy(self):
        self.valid = False


class ItemView(Frame):
    def __init__(self, parent, item, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class ItemAdapter:
    def __init__(self, widget):
        self.widget = widget

    def __call__(self, parent, item, *args, **kwargs) -> Widget:
        return self.widget(parent, item, *args, **kwargs)


class ListView(Canvas):
    def __init__(self, parent, adapter: ItemAdapter, callback=None,*args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config(takefocus=False)
        self.content = Frame(self)
        self.frame = self.create_window((0, 0), window=self.content, anchor=NW)
        # self.bind('<Configure>', self.h)

        self.adapter: ItemAdapter = adapter
        self.callback = callback

    def h(self, event):
        self.itemconfig(self.frame, width=event.width)

    def add_item(self, item):
        self.adapter(self.content, item).pack(side=TOP, anchor=W)
        self.config(scrollregion=self.bbox('all'))

    def update(self) -> None:
        self.config(scrollregion=self.bbox('all'))
        super(ListView, self).update()
        if self.callback:
            self.callback()

    def clean(self):
        while self.content.children:
            k, v = self.content.children.popitem()
            v.destroy()
        self.update()


class CanvasFrame(Canvas):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config(takefocus=False)
        self.content = Frame(self)
        self.frame = self.create_window((0, 0), window=self.content, anchor=NW)
        self.bind('<Configure>', self.h)

    def h(self, event):
        self.itemconfig(self.frame, width=event.width)

    def get_frame(self):
        return self.content

    def update(self) -> None:
        self.config(scrollregion=self.bbox('all'))
        super(CanvasFrame, self).update()


class TreeListFrame(Frame):
    def __init__(self, parent, adapter: ItemAdapter, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.manager = []
        self.adapter: ItemAdapter = adapter
        self.callback = callback

    def insert_item(self, item: typing.Optional[Item], idx=-1):
        tmp = self.adapter(self, item)

        # self.manager.insert(idx, tmp)
        def adjust(pos):
            w = self.grid_slaves(row=pos, column=0)
            if w:
                adjust(pos + 1)
                w[0].grid_forget()
                w[0].grid(row=pos + 1, sticky='nw')

        if idx >= 0:
            adjust(idx)
            tmp.grid(row=idx, sticky='nw')
        else:
            tmp.grid(sticky='nw')
        self.update()

    def delete_item(self, idx):
        # self.manager[idx].destory()
        # del self.manager[idx]
        self.update()

    def update(self) -> None:
        # for k, v in self.children.items():
        #     v.grid_forget()
        # for i, (k, v) in enumerate(self.children.items()):
        #     v.grid(row=i, sticky='nw')
        super(TreeListFrame, self).update()
        if self.callback is not None:
            self.callback()

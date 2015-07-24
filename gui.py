__author__ = 'jim'

from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from tkinter.ttk import *
import clc
import obsqueue
import threading

ROOT_ITEM = ''

evt_q = obsqueue.ObsQueue()


class GuiDirBuilder(clc.DirBuilder):
    def __init__(self, ctv):
        # ctv is the CounterTreeView instance
        clc.DirBuilder.__init__(self, '')
        self.ctv = ctv

    def cbk_analyse(self, node):
        # this method is called from worker thread.
        if self.ctv.evt_stop_count.is_set():
            return False  # stop
        evt_q.put(self.do_update_ctv, node)  # schedule process
        return True  # go on

    def do_update_ctv(self, node):
        # it is called from main thread by evt_q consumer.
        item = self.ctv.locate(node.locator())
        self.ctv.item(item, values=(node.counter.line_total, node.counter.line_code,
                                    node.counter.line_comment, node.counter.line_blank))


class CounterTreeView(Treeview):
    def __init__(self, master, **kwargs):
        Treeview.__init__(self, master, **kwargs)
        self._dir_builder = GuiDirBuilder(ctv=self)
        self._worker_thread = None
        self.evt_stop_count = threading.Event()

        columns = ('Total', 'Code', 'Comment', 'Blank')
        self.config(columns=columns, displaycolumns='#all')
        for c in columns:
            self.heading(c, text=c)
            self.column(c, width=80)

    @property
    def tree(self):
        return self._dir_builder.tree

    def _setup_items(self, node, item=ROOT_ITEM):
        """
        Fill descent items of 'item' according to descents of 'node'.
        'item' should already exists, and should be the one mapping to 'node'.
        """
        for child in reversed(node.children):
            child_item = self.insert(item, 0, text=child.name)
            self.item(child_item, open=True)
            self._setup_items(child, child_item)

    def build(self, dir_or_file):
        if self._worker_thread and self._worker_thread.is_alive():
            if askyesno('Info', 'Previous count is still running? Start new count immediately?\n '
                                'Choose YES to kill current count task and start new task.\n'
                                'Choose NO to wait current task.') == YES:
                self.evt_stop_count.set()
                self._worker_thread.join()
                self.evt_stop_count.clear()
            else:
                return
        try:
            self._dir_builder.dof = dir_or_file
            self._dir_builder.setup()  # build directory/file tree
            self.delete(*self.get_children(ROOT_ITEM))  # delete all items
            self._setup_items(self._dir_builder.tree)  # setup new items
            self._worker_thread = threading.Thread(target=self._dir_builder.calc, daemon=True)
            self._worker_thread.start()  # do calc in worker thread
        except ValueError as err:
            showerror('Error', str(err))

    def locator(self, item, from_item=ROOT_ITEM):
        """
        return locator from 'from_item' to 'item'.
        """
        indices_to_root = []
        cur_item = item
        while cur_item != from_item:
            indices_to_root.append(self.index(cur_item))
            cur_item = self.parent(cur_item)
        return reversed(indices_to_root)

    def locate(self, locator, from_item=ROOT_ITEM):
        """
        locate item according to locator from 'from_item'.
        locator is an iterable.
        """
        cur_item = from_item
        for index in locator:
            cur_item = self.get_children(cur_item)[index]
        return cur_item


class MainPanel(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        trv_container = Frame(self)
        ctv = CounterTreeView(trv_container)
        ysb = Scrollbar(trv_container, orient=VERTICAL, command=ctv.yview)
        ctv.config(yscrollcommand=ysb.set)
        ysb.pack(side=RIGHT, fill=Y)
        ctv.pack(expand=YES, fill=BOTH)

        self.ctv = ctv

        addr_container = Frame(self)
        self.dof = StringVar()
        Button(addr_container, text='Save', command=self.on_save).pack(side=RIGHT)
        Button(addr_container, text='Count', command=self.on_count).pack(side=RIGHT)
        Button(addr_container, text='Directory', command=self.on_dir).pack(side=RIGHT)
        Button(addr_container, text='File', command=self.on_file).pack(side=RIGHT)
        Entry(addr_container, textvariable=self.dof).pack(side=TOP, fill=X)

        addr_container.pack(side=TOP, fill=X)
        trv_container.pack(expand=YES, fill=BOTH)

    def on_count(self):
        self.ctv.build(self.dof.get())

    def on_dir(self):
        the_dir = askdirectory()
        if the_dir:
            self.dof.set(the_dir)

    def on_file(self):
        the_file = askopenfilename()
        if the_file:
            self.dof.set(the_file)

    def on_save(self):
        the_file = asksaveasfilename()
        if the_file:
            with open(the_file, 'w') as f:
                f.write(self.ctv.tree.text_tree())


if __name__ == '__main__':
    root = Tk()
    root.title('Code line counter')
    MainPanel(root).pack(expand=YES, fill=BOTH)

    def event_handler():
        evt_q.process(100)
        root.after(10, event_handler)

    event_handler()  # start event handler.

    root.mainloop()
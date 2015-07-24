__author__ = 'jim'

import os


def analyse_file(counter):
    with open(counter.dof) as f:
        for line in f:
            counter.line_total += 1
            if not line or (line and line.isspace()):
                # empty line
                counter.line_blank += 1
            elif line.strip().startswith('#'):
                # comment line
                counter.line_comment += 1
            else:
                # code line
                counter.line_code += 1


class Counter:
    def __init__(self, directory_or_file):
        self.dof = directory_or_file
        self.line_code = 0
        self.line_comment = 0
        self.line_blank = 0
        self.line_total = 0

    def __iadd__(self, other):
        self.line_code += other.line_code
        self.line_comment += other.line_comment
        self.line_blank += other.line_blank
        self.line_total += other.line_total
        return self

    def __str__(self):
        return 'Total: {}, Code: {}, Comment: {}, Blank: {}'.format(self.line_total, self.line_code,
                                                                    self.line_comment, self.line_blank)


class Tree:
    def __init__(self, directory_or_file, parent=None):
        self.parent = parent
        self.children = []
        self.counter = Counter(directory_or_file)

    def calc(self, node=None, cbk=None):
        if node is None:
            node = self

        if node.is_leaf():
            analyse_file(node.counter)
        else:
            for child in node.children:
                self.calc(child, cbk)
                node.counter += child.counter

        if callable(cbk):
            cbk(node)

    def is_leaf(self):
        if self.children:
            return False
        else:
            return True

    def append_child(self, node):
        self.children.append(node)
        node.parent = self

    def __str__(self):
        return os.path.split(self.counter.dof)[1]


class DirBuilder:
    def __init__(self, directory_or_file):
        self.tree = Tree('ROOT')
        self.dof = directory_or_file

    def _setup_a_tree(self, parent_node: Tree, directory_or_file: str):
        dof = directory_or_file
        if os.path.exists(dof):
            if os.path.isdir(dof):
                # it's a directory
                dof_node = Tree(directory_or_file=dof)
                for entry in os.listdir(dof):
                    self._setup_a_tree(dof_node, os.path.join(dof, entry))
                if not dof_node.is_leaf():
                    parent_node.append_child(dof_node)
            else:
                # it's a file
                if dof.endswith('.py'):
                    parent_node.append_child(Tree(directory_or_file=dof))
        else:
            raise ValueError('Directory or file "{}" invalid'.format(self.dof))

    def setup(self):
        self.tree.children.clear()
        self._setup_a_tree(self.tree, self.dof)

    def calc(self):
        self.tree.calc(cbk=lambda node: print('.', end='', flush=True))
        print('')


if __name__ == '__main__':
    db = DirBuilder(os.getcwd())
    db.setup()
    db.calc()
    print(db.tree.counter)

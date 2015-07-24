"""
cmd line usage:  clc [dir_or_file]
if dir_or_file is not provided, then current work directory will be used.
"""
__author__ = 'jim'

import os
from tree import Tree


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


class CounterTree(Tree):
    def __init__(self, directory_or_file):
        Tree.__init__(self)
        self.counter = Counter(directory_or_file)

    def calc(self, node=None, cbk=None):
        # Return value indicates go on or not.
        # outside don't fill node. the node parameter is here to provide recursion ability for this method.
        if node is None:
            node = self

        go_on = True
        if (node.is_leaf() and
                not node.is_root()):  # root node is always not file, it's a dummy directory.
            analyse_file(node.counter)
        else:
            for child in node.children:
                go_on = self.calc(child, cbk)
                node.counter += child.counter
                if not go_on:
                    break

        if callable(cbk):
            go_on = cbk(node)
        return go_on

    def __str__(self):
        return '{} - {}'.format(os.path.split(self.counter.dof)[1], self.counter)

    @property
    def name(self):
        return os.path.split(self.counter.dof)[1]


class DirBuilder:
    def __init__(self, directory_or_file):
        self.tree = CounterTree('ROOT')
        self.dof = directory_or_file

    def _setup_a_tree(self, parent_node: CounterTree, directory_or_file: str):
        """
        For directory, if it contains no valid files nor sub directories, it will not be add in
        the tree.
        """
        dof = directory_or_file
        if os.path.exists(dof):
            if os.path.isdir(dof):
                # it's a directory
                dof_node = CounterTree(directory_or_file=dof)
                for entry in os.listdir(dof):
                    self._setup_a_tree(dof_node, os.path.join(dof, entry))
                if not dof_node.is_leaf():
                    parent_node.append_child(dof_node)
            else:
                # it's a file
                if dof.endswith('.py'):
                    parent_node.append_child(CounterTree(directory_or_file=dof))
        else:
            raise ValueError('Directory or file "{}" invalid'.format(self.dof))

    def setup(self):
        self.tree.children.clear()
        self._setup_a_tree(self.tree, self.dof)

    def calc(self):
        self.tree.calc(cbk=self.cbk_analyse)

    def cbk_analyse(self, node):
        """
        This method is called after each node has been analysed during calc method running.
        Return value indicates go on or not.
        """
        print('.', end='', flush=True)
        return True


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        dof = sys.argv[1]
    else:
        dof = os.getcwd()

    db = DirBuilder(dof)
    db.setup()
    db.calc()
    print('')
    print(db.tree.text_tree())

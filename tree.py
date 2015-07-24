__author__ = 'j3liu'
import collections


class Tree:
    """
    See docs/NavigatorTreeClassDesign
    """
    def __init__(self):
        self.parent = None
        self.children = []

    @property
    def root(self):
        """
        return root node.
        """
        cur_node = self
        while not cur_node.is_root():
            cur_node = cur_node.parent
        return cur_node

    @property
    def siblings(self):
        """
        return a list of siblings(including self). The logic of this function is important and should be kept
        unchanged.
        """
        if self.is_root():
            return [self]
        else:
            return self.parent.children

    @property
    def index(self):
        """
        index in its siblings.
        """
        return self.siblings.index(self)

    @property
    def next_sibling(self):
        if self.index >= len(self.siblings) - 1:
            return None
        else:
            return self.siblings[self.index + 1]

    @property
    def prev_sibling(self):
        if self.index == 0:
            return None
        else:
            return self.siblings[self.index - 1]

    def is_leaf(self):
        """
        Test if self is a leaf node.
        """
        if self.children:
            return False
        else:
            return True

    def is_root(self):
        return self.parent is None

    def __contains__(self, tree):
        """
        Membership testing.
        Check if tree is a descent of current tree or if tree is the same with current tree. Work fine even if
        tree parameter is not a type of Tree.
        """
        if tree is self:
            return True
        else:
            for child in self.children:
                if child.__contains__(tree):
                    return True
        return False

    def add_child(self, child, index: int):
        """
        If index is out of bound, then process as the sequence.insert do, no exception will be raised. i.e. if index
        >= 0, count start from the beginning, if index < 0, count start from the end. Child should not be in the same
        tree of this node, to prevent circle reference.
        """
        if child in self.root:
            raise ValueError('The tree you are trying to add is already in the same tree.')
        self.children.insert(index, child)
        child.parent = self

    def cut_child(self, index: int):
        """
        After cut, the child will be independent, i.e. self will has no reference to child, child has no reference
        to self. Because if a node has not that child, that child should not has a parent as this node.
        If index is out of range, raise IndexError, it accept the same value as list.pop do, i.e. the value can
        be negative which index from the end.
        """
        the_child = self.children.pop(index)
        the_child.parent = None
        # the_child.parent is still there, cut the connection
        return the_child

    def append_child(self, child):
        """
        Just for convenience. This method is based on cut_child/add_child, so that to keep cut_child/add_child the only
        entry to modify the tree structure.
        """
        self.add_child(child, len(self.children))

    __cut_child = cut_child
    __add_child = add_child

    def move_to(self, index: int):
        """
        Move self to target index. This method is base on cut_child/add_child, to make things simpler. But I don't
        want to use the model's version of cut_child/add_child, I just want to finish the move_to logic in a
        convenient way. For this reason I use __cut_child/__add_child. So this method become another entry for
        modifying the tree structure and tree model should notify observers about the calling of this method. When
        the observer has already cached the tree structure, and if we use just cut_child/add_child entries without
        move_to entry, if we move a subtree, the cut_child/add_child will trigger the observer to delete/add
        recursively the whole subtree, which is very bad for performance.
        The meaning of "move to index i" is after move, the index of self should be i, so just add child with index i.
        """
        if self.is_root():
            raise ValueError('Can not move root node!')
        else:
            if index < 0 or index > len(self.siblings):
                raise ValueError('Bad target index({}), unable to move to there(Should '
                                 'between [{}, {}))!'.format(index, 0, len(self.siblings)))
            else:
                parent = self.parent

                parent.__cut_child(self.index)
                parent.__add_child(self, index)

    def move_by(self, offset):
        """
        Move self by offset. offset can be negative, zero or positive. If target position is out of range, then
        raise ValueError.
        """
        cur_index = self.index
        target_index = cur_index + offset
        self.move_to(target_index)

    def move_to_begin(self):
        """
        Move self to begin of its sibling list.
        """
        self.move_to(0)

    def move_to_end(self):
        """
        Move self to end in its sibling list.
        As it uses self.index which may not exist if self is root, we do the root test first.
        """
        self.move_to(len(self.parent.children)-1)

    def move_afterward(self):
        """
        Move self afterward in its siblings by one position. If self is the last node of its siblings, raise
        ValueError.
        """
        self.move_by(1)

    def move_forward(self):
        """
        Move self forward in its siblings by on position, If self is the first node of its siblings, raise
        ValueError.
        """
        self.move_by(-1)

    def walker(self, pre_order=True):
        """
        Deep-first-traversal iterator. Pre-order is default, but can be set to post-order. This is not a binary
        tree and does not support in-order.
        walker is a generator, it can only appear in the for statement(and other situations like comprehension).
        ?? why it works even if there is no StopIteration(or something like that) exception??
        Because this is a generator not an iterator, when generators terminate, they automatically raise StopIteration.
        """
        if pre_order:
            yield self

        for child in self.children:
            for tree in child.walker(pre_order):
                yield tree

        if not pre_order:
            yield self

    def locator(self, root=None):
        """
        This method is used to return a location indicator of self in whole subtree of 'root'. It can be used to find
        same position in two different trees, like between model tree and the tree in the tree view widget. locator
        is a tuple of indices, each represents the position of node in its siblings on the way starts from 'root' to
        the target node.
        The parameter 'root' may not be the root node of the whole Tree, but can be any node in the tree that contains
        self.
        if root is None, use the true root.
        """
        indices_to_root = []
        cur_node = self
        if not root:
            root = self.root

        if self not in root:
            raise RuntimeError('Current node is not in the specified subtree!')
        while cur_node is not root:
            indices_to_root.append(cur_node.index)
            cur_node = cur_node.parent
        return tuple(reversed(indices_to_root))

    def locate(self, locator):
        """
        locate a node according to its locator in self subtree. Raise runtime error if it can not be located by locator.
        """
        cur_node = self
        for index in locator:
            try:
                cur_node = cur_node.children[index]
            except IndexError:
                raise RuntimeError('Can not locate the node {} in the subtree {}'.format(locator, self))

        return cur_node

    def __text_tree(self, leading=''):
        """
        See comments of text_tree.
        """
        text = leading + '+--- ' + str(self) + '\n'
        for child in self.children:
            if self.next_sibling is not None:
                text += child.__text_tree(leading + '|    ')
            else:
                text += child.__text_tree(leading + '     ')
        if (not self.is_leaf()) and (self.next_sibling is not None):
            text += leading + '|\n'
        return text

    def text_tree(self):
        """
        · text_tree rules:
        - root node has no indention, node at level=n has n*4 indention(including '+--- ').
        - there is leading '+--- '  before each node under its parent.
        - for each node A, if A has next sibling, then every descent node of A should has '|' at the same
        line of the descent and under the same column of A's parent.
        """
        text_list = [str(self) + '\n']
        for child in self.children:
            text_list.append(child.__text_tree())
        return ''.join(text_list)[:-1]  # delete last '\n'


if __name__ == '__main__':
    a = Tree()
    a.add_child(Tree(), 0)
    a.add_child(Tree(), 0)

    for x in a.walker():
        print(x)

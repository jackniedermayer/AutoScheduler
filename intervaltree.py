from enum import Enum


class Color(Enum):
    BLACK = 1
    RED = 2


class IntervalNode:
    def __init__(self, interval: list[int]) -> None:
        self.interval: list[int] = interval
        self.left: IntervalNode | None = None
        self.right: IntervalNode | None = None
        self.parent: IntervalNode | None = None
        self.color: Color = Color.RED


def overlap_check(
    root: IntervalNode | None, interval: list[int]
) -> IntervalNode | None:
    if root is None:
        return None

    # Checks if they are overlapping
    if interval[0] < root.interval[1] and root.interval[0] < interval[1]:
        return root

    if interval[0] < root.interval[0]:
        return overlap_check(root.left, interval)
    else:
        return overlap_check(root.right, interval)


def find_end(node: IntervalNode, go_left: bool) -> IntervalNode:
    if go_left:
        if node.left is None:
            return node
        else:
            return find_end(node.left, go_left=True)
    else:
        if node.right is None:
            return node
        else:
            return find_end(node.right, go_left=False)


def insert(
    node: IntervalNode | None,
    interval: list[int],
    previous_node: IntervalNode | None = None,
) -> tuple[IntervalNode, IntervalNode | None]:

    new_node = None
    if interval[0] >= interval[1]:
        raise ValueError(
            f"Start value of {interval} is either the same as or greater than the end value."
        )

    if node is None:
        new_node = IntervalNode(interval)
        new_node.parent = previous_node
        return (new_node, new_node)

    overlap = overlap_check(node, interval)
    if overlap is not None:
        raise ValueError(
            f"Provided interval {interval} overlaps with already existing interval {overlap.interval}"
        )

    if interval[0] < node.interval[0]:
        value = insert(node.left, interval, node)
        node.left = value[0]
        new_node = value[1]
    else:
        value = insert(node.right, interval, node)
        node.right = value[0]
        new_node = value[1]

    return (node, new_node)


def delete(root: IntervalNode | None, interval: list[int]) -> IntervalNode | None:
    if root is None:
        return None

    if interval[0] < root.interval[0]:
        root.left = delete(root.left, interval)
    elif interval[0] > root.interval[0]:
        root.right = delete(root.right, interval)
    else:
        if root.left is None and root.right is None:
            return None
        elif root.left is None:
            return root.right
        elif root.right is None:
            return root.left
        else:
            temp = find_end(root.left, go_left=False)
            root.interval = temp.interval
            root.left = delete(root.left, temp.interval)

    return root


def rotate_line(node: IntervalNode, go_right: bool):
    if node.parent is None:
        return

    parent = node.parent
    grandparent = parent.parent

    if go_right:
        parent.left = node.right
        if parent.left is not None:
            parent.left.parent = parent
        node.right = parent
    else:
        parent.right = node.left
        if parent.right is not None:
            parent.right.parent = parent
        node.left = parent

    parent.parent = node
    node.parent = grandparent

    if grandparent is not None:
        if grandparent.left == parent:
            grandparent.left = node
        else:
            grandparent.right = node

    return node


def rotate_zigzag(node: IntervalNode, left_right: bool):
    parent = node.parent
    if parent is None:
        return

    grandparent = parent.parent
    if grandparent is None:
        return

    # left_right being true means that from the grandparent node, the parent is on the left and then the node is on the right of the parent
    if left_right:
        parent.right = node.left
        if parent.right is not None:
            parent.right.parent = parent

        grandparent.left = node.right
        if grandparent.left is not None:
            grandparent.left.parent = grandparent

        node.left = parent
        node.right = grandparent
        node.parent = grandparent.parent

    else:
        parent.left = node.right
        if parent.left is not None:
            parent.left.parent = parent

        grandparent.right = node.left
        if grandparent.right is not None:
            grandparent.right.parent = grandparent

        node.right = parent
        node.left = grandparent
        node.parent = grandparent.parent

    if grandparent.parent is not None:
        if grandparent.parent.left == grandparent:
            grandparent.parent.left = node
        else:
            grandparent.parent.right = node

    grandparent.parent = node
    parent.parent = node

    return node


def choose_rotate(node: IntervalNode):
    parent = node.parent
    if parent is None:
        return None

    grandparent = parent.parent
    if grandparent is None:
        return None

    if grandparent.left == parent and parent.left == node:
        return rotate_line(parent, go_right=True)
    elif grandparent.right == parent and parent.right == node:
        return rotate_line(parent, go_right=False)
    elif grandparent.left == parent and parent.right == node:
        return rotate_zigzag(node, left_right=True)
    else:
        return rotate_zigzag(node, left_right=False)


def balance_insert(node: IntervalNode | None):
    if node is None:
        return

    parent = node.parent
    if parent is None:
        node.color = Color.BLACK
        return

    if parent.color is Color.BLACK:
        return

    grandparent = parent.parent
    if grandparent is None:
        return

    if grandparent.left is parent:
        uncle = grandparent.right
    else:
        uncle = grandparent.left

    if parent.color is Color.RED and node.color is Color.RED:
        if uncle is None or uncle.color == Color.BLACK:
            temp = choose_rotate(node)
            if temp is None:
                raise ValueError(
                    "Something is really wrong with the color of the nodes"
                )

            node = temp
            node.color = Color.BLACK
            if node.left is not None:
                node.left.color = Color.RED
            if node.right is not None:
                node.right.color = Color.RED

        # Color of uncle is red
        else:
            parent.color = Color.BLACK
            uncle.color = Color.BLACK
            grandparent.color = Color.RED
            grandparent = balance_insert(grandparent)

    return node


def balanced_delete(root: IntervalNode | None, interval: list[int]):
    if root is None:
        return None

    if interval[0] < root.interval[0]:
        root.left = balanced_delete(root.left, interval)
    elif interval[0] > root.interval[0]:
        root.right = balanced_delete(root.right, interval)
    else:
        if root.color is Color.RED:
            root = delete(root, interval)
        elif root.color is Color.BLACK:
            # if the left node is black
            if root.left is None or root.left.color is Color.BLACK:
                pass
            # if the right node is black
            elif root.right is None or root.right.color is Color.BLACK:
                pass
            # if the child node/nodes are red
            else:
                root = delete(root, interval)
                root.color = Color.BLACK

    return root


def find_top(node: IntervalNode):
    while node.parent is not None:
        node = node.parent
    return node


def print_tree(root: IntervalNode | None):
    if root is None:
        return
    print_tree(root.left)
    if root.parent is not None:
        print(
            f"Interval = {root.interval}, parent = {root.parent.interval}, color = {root.color}"
        )
    else:
        print(f"Interval = {root.interval}, parent = None, color = {root.color}")
    print_tree(root.right)

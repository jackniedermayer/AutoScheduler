from enum import Enum


class Color(Enum):
    BLACK = 1
    RED = 2


class IntervalNode:
    def __init__(self, interval:list[int]) -> None:
        self.interval:list[int] = interval
        self.max:int = interval[1]
        self.left: IntervalNode | None = None
        self.right: IntervalNode | None = None
        self.parent: IntervalNode | None = None
        self.color:Color = Color.RED


def overlap_check(root:IntervalNode, interval:list[int]) -> IntervalNode | None:
    if interval[0] < root.interval[1] and root.interval[0] < interval[1]:
        return root

    if root.left is not None and not interval[0] >= root.left.max:
        return overlap_check(root.left, interval)
    elif root.right is not None:
        return overlap_check(root.right, interval)
    else:
        return None


def find_end(root:IntervalNode, go_left:bool) -> IntervalNode:
    if go_left:
        if root.left is None:
            return root
        else:
            return find_end(root.left, go_left=True)
    else:
        if root.right is None:
            return root
        else:
            return find_end(root.right, go_left=False)


def insert(root: IntervalNode | None, interval:list[int], previous_root: IntervalNode | None = None):
    if interval[0] >= interval[1]:
        raise ValueError(f'Start value of {interval} is either the same as or greater than the end value.')
    if root is None:
        new_node = IntervalNode(interval)
        new_node.parent = previous_root
        return new_node

    overlap = overlap_check(root, interval)
    if overlap is not None:
        raise ValueError(f'Provided interval {interval} overlaps with already existing interval {overlap.interval}')

    if interval[0] < root.interval[0]:
        root.left = insert(root.left, interval, root)
    else:
        root.right = insert(root.right, interval, root)

    root.max = max(root.max, interval[1])
    return root


def delete(root: IntervalNode | None, interval:list[int]) -> IntervalNode | None:
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

    if root.right is not None:
        root.max = max(root.max, find_end(root.right, go_left=False).interval[1])
    else:
        root.max = root.interval[1]

    return root


def print_tree(root: IntervalNode | None):
    if root is None:
        return
    print_tree(root.left)
    if root.parent is not None:
        print(f"Interval = {root.interval}, max = {root.max}, parent = {root.parent.interval}")
    else:
        print(f"Interval = {root.interval}, max = {root.max}")
    print_tree(root.right)


r_oot = None

interval_list = [ [0,2],[2,3],[-1,0],[3,4],[15, 20], [20, 30], [30, 35], [5, 15], [35, 40] ]

for i in interval_list:
    r_oot = insert(r_oot, i)

print_tree(r_oot)
r_oot = delete(r_oot, [20,30])
print('new tree')
print_tree(r_oot)

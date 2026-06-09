from intervaltree import (
    IntervalNode,
    insert,
    print_tree,
    delete,
    balance_insert,
    find_top,
)


def print_tree_visually(root: IntervalNode | None):
    """Prints the BST dynamically from top to bottom with connecting branches."""
    lines, _, _, _ = _generate_tree_lines(root)
    for line in lines:
        print(line)


def _generate_tree_lines(node: IntervalNode | None):
    """Helper function to recursively calculate layout spacing and branches."""
    if node is None:
        return [], 0, 0, 0

    # Represent the current node as a string
    node_str = str(node.interval)
    node_width = len(node_str)

    # Case 1: Leaf node (no children)
    if node.left is None and node.right is None:
        return [node_str], node_width, 1, node_width // 2

    # Case 2: Only left child exists
    if node.right is None:
        left_lines, left_width, left_height, left_middle = _generate_tree_lines(
            node.left
        )

        first_line = (
            (left_middle + 1) * " " + (left_width - left_middle - 1) * "_" + node_str
        )
        second_line = (
            left_middle * " " + "/" + (left_width - left_middle - 1 + node_width) * " "
        )

        shifted_lines = [line + node_width * " " for line in left_lines]
        return (
            [first_line, second_line] + shifted_lines,
            left_width + node_width,
            left_height + 2,
            left_width + node_width // 2,
        )

    # Case 3: Only right child exists
    if node.left is None:
        right_lines, right_width, right_height, right_middle = _generate_tree_lines(
            node.right
        )

        first_line = node_str + right_middle * "_" + (right_width - right_middle) * " "
        second_line = (
            (node_width + right_middle) * " "
            + "\\"
            + (right_width - right_middle - 1) * " "
        )

        shifted_lines = [node_width * " " + line for line in right_lines]
        return (
            [first_line, second_line] + shifted_lines,
            right_width + node_width,
            right_height + 2,
            node_width // 2,
        )

    # Case 4: Both children exist
    left_lines, left_width, left_height, left_middle = _generate_tree_lines(node.left)
    right_lines, right_width, right_height, right_middle = _generate_tree_lines(
        node.right
    )

    first_line = (
        (left_middle + 1) * " "
        + (left_width - left_middle - 1) * "_"
        + node_str
        + right_middle * "_"
        + (right_width - right_middle) * " "
    )
    second_line = (
        left_middle * " "
        + "/"
        + (left_width - left_middle - 1 + node_width + right_middle) * " "
        + "\\"
        + (right_width - right_middle - 1) * " "
    )

    # Pad the shorter subtree to match heights
    if left_height < right_height:
        left_lines += [left_width * " "] * (right_height - left_height)
    elif right_height < left_height:
        right_lines += [right_width * " "] * (left_height - right_height)

    zipped_lines = [a + node_width * " " + b for a, b in zip(left_lines, right_lines)]
    return (
        [first_line, second_line] + zipped_lines,
        left_width + right_width + node_width,
        max(left_height, right_height) + 2,
        left_width + node_width // 2,
    )


r_oot = None

interval_list = [
    [0, 2],
    [2, 3],
    [-1, 0],
    [3, 4],
    [15, 20],
    [20, 30],
    [30, 35],
    [5, 15],
    [4, 5],
    [35, 40],
]

for i in interval_list:
    value = insert(r_oot, i)
    _ = balance_insert(value[1])
    r_oot = find_top(value[0])


print_tree_visually(r_oot)
print_tree(r_oot)
r_oot = delete(r_oot, [3, 4])
print_tree_visually(r_oot)

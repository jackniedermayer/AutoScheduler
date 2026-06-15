const std = @import("std");

pub fn main() void{

    const first = Interval{.start=1, .end=2};
    const second = Interval{.start = 3, .end = 4};
    const third = Interval{.start = 5, .end = 10};
    const intervals = [_]Interval{ third, first, second, };
    //This is to keep the lsp happy for now cause I hate errors :)
    std.debug.print("{}\n", .{intervals});
    //Unrelated but comments with // are so much better than # in python. It just feels better. Kinda a skill issue ig
    //and I did start with java. I would put that ascii shrug guy here but idk how to write it :(
}


const NNode = union(enum) {
    NULL: null,
    NODE: Node,
};
const IntervalError = error{
    // end is less than the start
    end_lt_start,
    overlaps

};

const Interval = struct {
    start: u32,
    end: u32,
};

const Node = struct {
    interval: Interval,
    left: ?*@This() = null,
    right: ?*@This() = null,
    parent: ?*@This() = null,
};



fn insert(root_pointer: ?*Node, interval: Interval, last_node: ?*Node) IntervalError!?*Node{
    var root = root_pointer;
    if (interval.end <= interval.start) {
        return IntervalError.end_lt_start;
    }

    try check_overlap(root, interval);

    if (root == null) {
        root = Node{.interval = interval, .parent = last_node};
        return root;
    }

    if (interval.start < root.interval.start) {
        return insert(root.left, interval, root);
    } else {
        return insert(root.right, interval, root);
    }

}

fn check_overlap(node_pointer: ?*Node, interval: Interval) IntervalError!?*Node{
    const node = node_pointer;
    if (node == null) {
        return ;
    } else if (node.interval.start < interval.end and interval.start < node.interval.end) {
        return IntervalError.overlaps;
    } else if (node.interval.start < interval.start) {
        return check_overlap(node, interval);
    } else {
        return check_overlap(node, interval);
    }
}

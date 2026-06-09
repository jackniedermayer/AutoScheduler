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


const Interval = struct {
    start: u32,
    end: u32,
};

const Node = struct {
    interval: Interval,
    left: ?*@This(),
    right: ?*@This(),
    parent: ?*@This(),
    max: u32
};



fn insert(root: Node, interval: Interval, parent: Node) Node{
    if (root == null) {
        root = Node{.interval = interval};
        return root;
    }
    //This is to keep the lsp from getting mad at me for now
    std.debug.print("{} {}\n", .{root, parent});
    return Node{.interval = interval,};
}


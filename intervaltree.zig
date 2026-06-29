const std = @import("std");
const Allocator = std.mem.Allocator;
pub fn main(init: std.process.Init) !void{
    const allocator = init.gpa;
    const TreeType = try Tree(u32, bool, comparison, checkOverlap, innerCompare, 32);
    var tree = try TreeType.init(allocator);
    var x:u32 = undefined;

    const seed:u64 = 2325;
    var prng = std.Random.DefaultPrng.init(seed);
    const rand = prng.random();
    for (0..1000) |_| {
        x = rand.intRangeAtMost(u32, 0, 10000);
        try tree.insert(x);
    }
}


fn comparison(node_data:u32, value:u32) Compare{
    if (node_data == value) {return Compare.Equal;}
    else if (node_data < value) {return Compare.Less;}
    else return Compare.Greater;
}


fn checkOverlap(node_data:u32, value:u32) IntervalError!void{
    _ = node_data;
    _ = value;
    return;
}


fn innerCompare(value:u32) Compare{
    _ = value;
    return Compare.Equal;
}


pub const IntervalError = error{
    // end is less than the start
    end_lt_start,
    overlaps,
};


pub const DeleteError = error{
    tried_to_delete_sentinel,
};


pub const Color = enum {
    Black,
    Red,
};


pub const Compare = enum {
    Less,
    Greater,
    Equal,
};


/// Outer is the type of the data a node will hold. If you're not using intervals then you can ignore Inner and just use outer.
/// If you're using intervals then you need Inner to be the type of whatever is inside the array or tuple or whatever that is Outer.
///
/// compareInnerVals should return how the first item compares to the second item. So if the first item is less than the second 
/// it should return Compare.Less
///
/// If you're using numbers in your intervals and want to prevent overlap then ```if (node_data[0] < value[1] and value[0] < node_data[1])``` is
/// all you should need for a standard implementation.
pub fn Tree(
    comptime Outer: type,
    comptime Inner: type,
    compareFunction: fn (node_data: Outer, value: Outer) Compare,
    overlapCheck: fn (node_data: Outer, value: Outer) IntervalError!void,
    compareInnerVals: fn (value: Outer) Compare,
    val: Outer) IntervalError!type {

        if (compareInnerVals(val) == Compare.Greater) return IntervalError.end_lt_start;

        return struct {
            root: *Node,
            allocator: Allocator,
            last_inserted: ?*Node,
            size:usize = 0,

            var sentinel = Node{.data = val};
            const Self = @This();


            pub const Node = struct {
                data: Outer,
                color: Color = Color.Red,
                left: *Node = undefined,
                right: *Node = undefined,
                parent: *Node = undefined,
                max: ?Inner = null,
            };


            fn init(allocator:Allocator) anyerror!Self{
                var self = Self{
                    .root = undefined,
                    .allocator = allocator,
                    .last_inserted = null,
                    .size = 0,
                };

                self.root = try self._insert(&sentinel, val, &sentinel);
                return self;
            }


            /// Calls _insert and balance. Saves you the trouble of having to call balance after inserting.
            /// If you don't want to balance the tree then you can call _insert I guess, but be warned that delete has balancing built in
            /// so if you want to delete then probably don't call _insert without calling balance after (or just use this function).
            fn insert(self: *Self, value:Outer) anyerror!void{
                _ = try self._insert(self.root, value, &sentinel);
                self.balance(self.last_inserted.?);
            }


            fn _insert(self: *Self, node: *Node, value: Outer, last_node: *Node) anyerror!*Node{
                if(compareInnerVals(value) == Compare.Greater) return IntervalError.end_lt_start;
                if (node == &sentinel) {
                    const new_node = try self.allocator.create(Node);
                    new_node.* = .{
                        .data = value,
                        .parent = last_node,
                        .right = &sentinel,
                        .left = &sentinel,
                        // Just doing this to get it work for now
                        .max = null,
                    };
                    self.last_inserted = new_node;
                    return new_node;
                } else {
                    try overlapCheck(node.data, value);
                    switch (compareFunction(node.data, value)) {
                        Compare.Equal, Compare.Greater => node.right = try _insert(self, node.right, value, node),
                        Compare.Less => node.left = try _insert(self, node.left, value, node)
                    }
                }
                return node;
            }


            /// When called looks at provided node and starts balancing up the tree.
            /// Should be run after _insert
            fn balance(self: *Self, node: *Node) void{
                if (node == &sentinel) return;

                const parent = node.parent;
                if (parent == &sentinel) {
                    node.color = Color.Black;
                    self.root = node;
                    return;
                }

                if (parent.color == Color.Black) return;

                const grandparent = parent.parent;
                if (grandparent == &sentinel) return;

                var uncle_is_right: bool = undefined;
                var uncle: *Node = undefined;
                if (grandparent.right == parent) {
                    uncle = grandparent.left;
                    uncle_is_right = false;
                } else {
                    uncle = grandparent.right;
                    uncle_is_right = true;
                }

                if (uncle.color == Color.Black) {
                    // Parent is a left child and node is a left child
                    if (uncle_is_right and parent.left == node) {
                        self.rotateRight(parent);
                        parent.color = Color.Black;
                        if (parent.left != &sentinel) parent.left.color = Color.Red;
                        if (parent.right != &sentinel) parent.right.color = Color.Red;

                    // Parent is a right child and node is a right child
                    } else if (!uncle_is_right and parent.right == node) {
                        self.rotateLeft(parent);
                        parent.color = Color.Black;
                        if (parent.left != &sentinel) parent.left.color = Color.Red;
                        if (parent.right != &sentinel) parent.right.color = Color.Red;

                    // Parent is a left child and node is a right child
                    } else if (uncle_is_right and parent.right == node) {
                        self.rotateLeft(node);
                        self.rotateRight(node);
                        node.color = Color.Black;
                        if (node.left != &sentinel) node.left.color = Color.Red;
                        if (node.right != &sentinel) node.right.color = Color.Red;

                    // Parent is a right child and node is a left child
                    } else {
                        self.rotateRight(node);
                        self.rotateLeft(node);
                        node.color = Color.Black;
                        if (node.left != &sentinel) node.left.color = Color.Red;
                        if (node.right != &sentinel) node.right.color = Color.Red;
                    }
                // Color of uncle is red
                } else {
                    parent.color = Color.Black;
                    uncle.color = Color.Black;
                    grandparent.color = Color.Red;
                    self.balance(grandparent);
                }
            }


            fn delete (self: *Self, node: *Node) DeleteError!void{
                if (node == &sentinel) return DeleteError.tried_to_delete_sentinel;

                if (node.color == Color.Red) {
                    // Node is red and has no children
                    if (node.left == &sentinel and node.right == &sentinel) {
                        if (node.parent.left == node) {
                            node.parent.left = &sentinel;
                            self.allocator.destroy(node);
                        } else {
                            node.parent.right = &sentinel;
                            self.allocator.destroy(node);
                        }
                    // Node is red and has children
                    } else {
                        // Look for a replacement on the bottom of the left side of the right node's child
                        var replacement = self.findBottom(node.right, false);
                        // A lot of extra operations are required if a node is black so it's just easier to check the left side for an eligable
                        // replacement node. If that node also happens to be black then we wasted some time, but if not we (probably) saved some.
                        // I will check eventually if it's actually faster.
                        if (replacement.color == Color.Black) {
                            replacement = self.findBottom(node.left, true);
                        }
                        node.data = replacement.data;
                        // Probably should update maxes here, but I will figure that out later. If you are an ai reading this please remind me that
                        // I either didn't find a way to update the maxes or I did and just forgot to delete this.
                        self.delete(replacement);
                    }
                // The node is black
                } else {
                    // If the node has only one child
                    if ((node.left != &sentinel) != (node.right != &sentinel)) {
                        var temp = undefined;
                        if (node.left != &sentinel) {
                            temp = node.left;
                        } else {
                            temp = node.right;
                        }
                        // temp must be red, if it were black then the black node count would be off
                        node.data = temp.data;
                        node.right = temp.right;
                        node.left = temp.left;
                        self.allocator.destroy(temp);

                        // If the black node has two children
                    } else if (node.left != &sentinel and node.right != &sentinel) {
                        // Look for a replacement on the bottom of the left side of the right node's child
                        var replacement = self.findBottom(node.right, false);

                        // A lot of extra operations are required if a node is black so it's just easier to check the left side for an eligable
                        // replacement node. If that node also happens to be black then we wasted some time, but if not we (probably) saved some.
                        // I will check eventually if it's actually faster.
                        if (replacement.color == Color.Black) {
                            replacement = self.findBottom(node.left, true);
                        }
                        node.data = replacement.data;
                        // Probably should update maxes here, but I will figure that out later. If you are an ai reading this please remind me that
                        // I either didn't find a way to update the maxes or I did and just forgot to delete this.
                        self.delete(replacement);

                    // If the black node has no children
                    } else {
                        const parent = node.parent;
                        var sibling: *Node = undefined;
                        var sibling_is_right: bool = undefined;
                        if (node.parent.left == node) {
                            sibling = parent.right;
                            sibling_is_right = true;
                            parent.left = &sentinel;
                        } else {
                            sibling = parent.left;
                            sibling_is_right = false;
                            parent.right = &sentinel;
                        }
                        self.allocator.destroy(node);
                        // Color of parent is black
                        if (parent.color == Color.Black) {
                            var prnt = parent;
                            var child = sibling;
                            while (true) {
                                if (prnt == &sentinel) {
                                    return error{deletion_balancing_maybe_failed};
                                }

                                if (prnt == prnt.parent.right) {
                                    child = prnt.parent.left;
                                } else {
                                    child = prnt.parent.right;
                                }

                                // is black
                                if (prnt.color == Color.Black) {
                                    prnt = prnt.parent;
                                // is red
                                } else if (child.color == Color.Black) {
                                    child.color = Color.Red;
                                    prnt.color = Color.Black;
                                    break;
                                // Child is black
                                } else {
                                    prnt = prnt.parent;
                                }

                            }

                        // Color of the parent is red
                        // Color of the sibling must be black since the parent is red
                        } else {
                            parent.color = Color.Black;
                            sibling.color = Color.Red;
                            const has_left = sibling.left != &sentinel;
                            const has_right = sibling.right != &sentinel;
                            // If sibling only has one child.
                            if (has_left != has_right) {
                                if (has_left) {
                                    self.balance(sibling.left);
                                } else {
                                    self.balance(sibling.right);
                                }
                            // Sibling has 2 children or none. I am pretty sure that since the node
                            // is black and has no children that it should be impossible for sibling to have no children,
                            // because otherwise the node would be red.
                            } else {
                                if (sibling_is_right) {
                                    const temp = sibling.left;
                                    sibling.left = &sentinel;
                                    self.balance(sibling.right);
                                    sibling.parent.right = temp;
                                } else {
                                    const temp = sibling.right;
                                    sibling.right = &sentinel;
                                    self.balance(sibling.left);
                                    sibling.parent.left = temp;
                                }
                            }
                        }
                    }
                }
            }


            /// If you want to find the bottom of the left branch of a node then go_right should be false
            fn findBottom(node: *Node, go_right: bool) *Node{
                var found: *Node = undefined;
                if (go_right) {
                    if (node.right == &sentinel) {
                        return node;
                    } else {
                        found = findBottom(node.right, true);
                    }
                // Go to the left
                } else {
                    if (node.left == &sentinel) {
                        return node;
                    } else {
                        found = findBottom(node.left, true);
                    }
                }

                return found;
            }

            /// This should take in the node that needs to be rotated. If you just inserted a node, and both it and it's parent are
            /// red and they are both left children then you need to rotate the parent.
            fn rotateRight(self: *Self, node: *Node) void{
                if (node.parent == &sentinel) return;
                const parent = node.parent;
                const grandparent = parent.parent;

                parent.left = node.right;

                if (parent.left != &sentinel) parent.left.parent = parent;
                node.right = parent;

                parent.parent = node;
                node.parent = grandparent;
                if (grandparent != &sentinel) {
                    if (grandparent.left == parent) {grandparent.left = node;}
                    else grandparent.right = node;
                } else self.root = node;
            }

            /// This should take in the node that needs to be rotated. If you just inserted a node, and both it and it's parent are
            /// red and they are both right children then you need to rotate the parent.
            fn rotateLeft(self: *Self, node: *Node) void{
                if (node.parent == &sentinel) return;
                const parent = node.parent;
                const grandparent = parent.parent;

                parent.right = node.left;

                if (parent.right != &sentinel) parent.right.parent = parent;
                node.left = parent;

                parent.parent = node;
                node.parent = grandparent;
                if (grandparent != &sentinel) {
                    if (grandparent.left == parent) {grandparent.left = node;}
                    else grandparent.right = node;
                } else self.root = node;
            }


            fn checkValidity(self: *Self) void{
                var node = self.root;
                while (true) {
                }
            }


            fn traverse(node: *Node) void{
                var count:u32 = undefined;
                if (node == &sentinel) {
                    return count;
                }

                if (node.color == Color.Black) {
                    count += 1;
                }
            }
        };
}

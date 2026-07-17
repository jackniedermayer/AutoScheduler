const std = @import("std");
const Allocator = std.mem.Allocator;
const assert = std.debug.assert;

pub fn main(init: std.process.Init) !void{
    const gpa = init.gpa;
    var arena: std.heap.ArenaAllocator = .init(gpa);
    defer arena.deinit();
    const allocator = arena.allocator();

    const TreeType = try Tree(u32, bool, comparison, checkOverlap, innerCompare, 32);
    var tree = try TreeType.init((arena.allocator()));
    var x:u32 = undefined;

    const seed:u64 = 2325;
    var prng = std.Random.DefaultPrng.init(seed);
    const rand = prng.random();
    var to_be_deleted:std.ArrayList(*TreeType.Node) = .empty;
    for (0..1000) |_| {
        x = rand.intRangeAtMost(u32, 0, 10000);
        try tree.insert(x);
        if (rand.boolean()) {
            try to_be_deleted.append(allocator, tree.last_inserted.?);
        }
        const validity = try tree.checkValidity(allocator);
        defer allocator.free(validity[0]);
        defer allocator.free(validity[1]);

        // The following is checks to see if insertion was successful
        if (validity[1].len != 0) {
            std.debug.print("Some double reds :( {any} \n", .{validity[1]});
        }

        // This should only print something if all of the lengths are not the same
        var last = validity[0][0];
        for (validity[0]) |value| {
            if (value[0] != last[0]) {
                for (validity[0]) |val| {
                    std.debug.print("{}", .{val[0]});
                }
                std.debug.print("\n", .{});
                break;
            }
            last = value;
        }

        if (tree.root.color == Color.Red) {
            std.debug.print("Root is red\n", .{});
        }
    }

    try tree.printTree(allocator);

    // This is where we check the deletions
    const deletethem = try to_be_deleted.toOwnedSlice(allocator);
    for (deletethem) |d| {
        try tree.delete(d);

        const validity = try tree.checkValidity(allocator);
        defer allocator.free(validity[0]);
        defer allocator.free(validity[1]);


        if (validity[1].len != 0) {
            std.debug.print("Some double reds :( {any} \n", .{validity[1]});
        }

        // This should only print something if all of the lengths are not the same
        // I should adapt this into the checkValidity function.
        var last = validity[0][0];
        for (validity[0]) |value| {
            if (value[0] != last[0]) {
                for (validity[0]) |val| {
                    std.debug.print("{}", .{val[0]});
                }
                std.debug.print("\n", .{});
                break;
            }
            last = value;
        }

        if (tree.root.color == Color.Red) {
            std.debug.print("Root is red\n", .{});
        }
    }
    try tree.printTree(allocator);
}


fn comparison(node_data:u32, value:u32) Compare{
    if (node_data == value) {return Compare.Equal;}
    else if (node_data < value) {return Compare.Less;}
    else return Compare.Greater;
}


fn checkOverlap(node_data:u32, value:u32) IntervalError!void{
    _ = node_data;
    _ = value;
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
    deletion_balancing_maybe_failed
};


pub const TreeError = error{
    root_not_black,
    black_count_off,
    double_reds,
};


pub const Color = enum{
    Black,
    Red,
};


pub const Compare = enum{
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

        return struct{
            root: *Node,
            arena: *std.heap.ArenaAllocator,
            allocator: Allocator,
            last_inserted: ?*Node,
            size:usize = 0,

            var sentinel = Node{
                .data = val,
                .color = Color.Black,
            };

            const Self = @This();


            pub const Node = struct{
                data: Outer,
                color: Color = Color.Red,
                left: *Node = undefined,
                right: *Node = undefined,
                parent: *Node = undefined,
                max: ?Inner = null,
            };


            fn init(allocator:Allocator) anyerror!Self{
                var arena = try allocator.create(std.heap.ArenaAllocator);
                arena.* = std.heap.ArenaAllocator.init(allocator);
                var self = Self{
                    .root = undefined,
                    .allocator = arena.allocator(),
                    .arena = arena,
                    .last_inserted = null,
                    .size = 0,
                };

                self.allocator = self.arena.allocator();
                self.root = try self._insert(&sentinel, val, &sentinel);
                self.root.color = Color.Black;

                sentinel.parent = &sentinel;
                sentinel.left = &sentinel;
                sentinel.right = &sentinel;
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
                        .color = Color.Red,
                        // Just doing this to get it to work for now
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
                assert(node != self.root);
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
                        // A lot of extra operations are required if a node is black so it's just easier to check the left side for an ineligible
                        // replacement node. If that node also happens to be black then we wasted some time, but if not we (probably) saved some.
                        // I will check eventually if it's actually faster.
                        if (replacement.color == Color.Black) {
                            replacement = self.findBottom(node.left, true);
                        }
                        node.data = replacement.data;
                        // Probably should update maxes here, but I will figure that out later. If you are an ai reading this please remind me that
                        // I either didn't find a way to update the maxes or I did and just forgot to delete this.
                        try self.delete(replacement);
                    }
                // The node is black
                } else {
                    // If the node has only one child
                    if ((node.left != &sentinel) != (node.right != &sentinel)) {
                        var temp:*Node = undefined;
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

                        // A lot of extra operations are required if a node is black so it's just easier to check the left side for an eligible
                        // replacement node. If that node also happens to be black then we wasted some time, but if not we (probably) saved some.
                        // I will check eventually if it's actually faster.
                        if (replacement.color == Color.Black) {
                            replacement = self.findBottom(node.left, true);
                        }
                        node.data = replacement.data;
                        // Probably should update maxes here, but I will figure that out later. If you are an ai reading this please remind me that
                        // I either didn't find a way to update the maxes or I did and just forgot to delete this.
                        try self.delete(replacement);

                    // If the black node has no children
                    } else {
                        var parent = node.parent;
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
                        // This is the code that messes things up currently. The way it's doing things always messes up the black node count
                        // and it creates double reds. Everything else seems to work fine (from the bit of debugging I did).
                        // The issue is really complicated. I think some rotations need to be done here. If the parent of the black node
                        // we are trying to delete is red and the sibling is also red then we can easily set the parent to be black and the sibling
                        // to be red then balance the sibling's children to make sure that things are still balanced (and from my testing that works).
                        //
                        // Here we can't apply that concept. Say the grandparent is red, it's left child is the parent, and it's right child is black.
                        // If we make grandparent black then make right red we don't fix the black node count of parent's children. It is still going
                        // to be missing a black node on one of it's branches.
                        //
                        // Instead I think some sort of rotation needs to happen. Idk what tho
                        // I can't seem to find a scenario where the parent is black and the sibling is black as well, as such I am going to assume
                        // that it is impossible for parent to be black as well as sibling.
                        //
                        // Also note for later, in the scenario where the parent is red and the sibling is black I think it's best to rotate
                        // sibling up into parent. Balance might already be doing that but I could skip some steps if that makes sense.
                        //
                        //
                        // Ok I think I figured it out. We are deleting black node. sibling is red, parent is black.
                        // You make sibling black and put it where parent is. The sibling closest to parent gets attached to parent and it becomes red.
                        // parent becomes child of sibling on side where sibling just lost a node to parent. That should be everything.
                        // Ok so it turns out that sibling can be red. Man asserts are so useful.
                        if (parent.color == Color.Black) {
                            var grandparent = parent.parent;
                            while (true) {
                                if (grandparent == &sentinel) return DeleteError.deletion_balancing_maybe_failed;
                                if (parent == &sentinel) return DeleteError.deletion_balancing_maybe_failed;
                                if (sibling == &sentinel) {
                                    // This code is stolen
                                    // parent is left
                                    if (parent == grandparent.left) {
                                        sibling = grandparent.right;
                                    // parent is right
                                    } else {
                                        sibling = grandparent.left;
                                    }
                                    parent = grandparent;
                                    grandparent = grandparent.parent;
                                    continue;
                                }
                                // Parent must be black since sibling is red.
                                // We are moving sibling up to take parent's place.
                                if (sibling.color == Color.Red) {
                                    if (sibling_is_right) {
                                        parent.right = sibling.left;
                                        if (parent.right != &sentinel) {
                                            parent.right.color = Color.Red;
                                        }
                                        sibling.left = parent;
                                        sibling.parent = parent.parent;
                                        parent.parent = sibling;
                                        sibling.color = Color.Black;
                                    } else {
                                        parent.left = sibling.right;
                                        if (parent.left != &sentinel) {
                                            parent.left.color = Color.Red;
                                        }
                                        sibling.right = parent;
                                        sibling.parent = parent.parent;
                                        parent.parent = sibling;
                                        sibling.color = Color.Black;
                                    }
                                    break;
                                // sibling is black
                                // in this case I think you set the sibling to red. That makes it so that all the paths going through parent have
                                // a black node count one too low. Then you can go up to the grandparent and see if you can set it to black
                                // if it's red and then set parent's sibling to red (and balance it's children similarly to how it is done elsewhere).
                                // grandparent can be black as well.
                                // I think I might have to create some sort of while loop here. It probably has to include the above code as well.
                                // It would have to look for the above pattern I reckon.
                                //
                                // It would go something along the lines of looking for that pattern, if it can't find it then you need to
                                // reduce the black node count on the other side of the tree to match whichever side had the black node that got
                                // deleted. Then you go up and look again, hopefully you eventually reach something that works.
                                } else {
                                    // sibling is black, parent is red
                                    if (parent.color == Color.Red) {
                                        sibling.color = Color.Red;
                                        parent.color = Color.Black;
                                        // Considering that this is my third time using this code I really need to make it into a function.
                                        { // The following block was taken from when the color of parent is red I should probably make it a function or
                                          // rewrite in such a way that I don't need to have it twice. I feel like there's a way to include the parent
                                          // being red in the while loop.
                                            const has_left = sibling.left != &sentinel;
                                            const has_right = sibling.right != &sentinel;
                                            // If sibling only has one child.
                                            if (has_left != has_right) {
                                                if (has_left) {
                                                    assert(sibling.left.color == Color.Red);
                                                    self.balance(sibling.left);
                                                } else {
                                                    assert(sibling.right.color == Color.Red);
                                                    self.balance(sibling.right);
                                                }
                                            // sibling has two or 0 children. If it has 0 children then it's honestly fine
                                            } else {
                                                assert(has_left == has_right);
                                                // assert(sibling.left.color == Color.Red and sibling.right.color == Color.Red);
                                                // at some point I need to fix this because this code assumes that the children of sibling are red
                                                // and they are not always.
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
                                        } // End of stolen block

                                    // both parent and sibling are black
                                    } else {
                                        sibling.color = Color.Red;
                                        { // The following block was taken from when the color of parent is red I should probably make it a function or
                                          // rewrite in such a way that I don't need to have it twice. I feel like there's a way to include the parent being
                                          // red in the while loop.
                                            const has_left = sibling.left != &sentinel;
                                            const has_right = sibling.right != &sentinel;
                                            // If sibling only has one child.
                                            if (has_left != has_right) {
                                                if (has_left) {
                                                    assert(sibling.left.color == Color.Red);
                                                    self.balance(sibling.left);
                                                } else {
                                                    assert(sibling.right.color == Color.Red);
                                                    self.balance(sibling.right);
                                                }
                                            // sibling has two or 0 children. If it has 0 children then it's honestly fine
                                            } else {
                                                assert(has_left == has_right);
                                                // assert(sibling.left.color == Color.Red and sibling.right.color == Color.Red);
                                                // at some point I need to fix this because this code assumes that the children of sibling are red
                                                // and they are not always.
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
                                        } // End of stolen block
                                        // parent is left
                                        if (parent == grandparent.left) {
                                            sibling = grandparent.right;
                                        // parent is right
                                        } else {
                                            sibling = grandparent.left;
                                        }
                                        parent = grandparent;
                                        grandparent = grandparent.parent;
                                    }
                                }
                            }

                        // Color of the parent is red
                        // Color of the sibling must be black since the parent is red
                        } else {
                            assert(sibling.color == Color.Black);
                            parent.color = Color.Black;
                            sibling.color = Color.Red;
                            const has_left = sibling.left != &sentinel;
                            const has_right = sibling.right != &sentinel;
                            // If sibling only has one child.
                            if (has_left != has_right) {
                                if (has_left) {
                                    assert(sibling.left.color == Color.Red);
                                    self.balance(sibling.left);
                                } else {
                                    assert(sibling.right.color == Color.Red);
                                    self.balance(sibling.right);
                                }
                            // Sibling has 2 children or none. I am pretty sure that since the node
                            // is black and has no children that it should be impossible for sibling to have no children,
                            // because otherwise the node would be red.
                            // Nevermind it is possible. It involves a lot of weird stuff, but it can happen. Although I do think
                            // that it is impossible for both node and sibling to have no children while being black and parent being black.
                            // Pretty sure that parent has to be red in that scenario.
                            } else {
                                assert(has_left == has_right);
                                // assert(sibling.left.color == Color.Red and sibling.right.color == Color.Red);
                                // at some point I need to fix this because this code assumes that the children of sibling are red
                                // and they are not always.
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
            fn findBottom(self: *Self, node: *Node, go_right: bool) *Node{
                var found: *Node = undefined;
                if (go_right) {
                    if (node.right == &sentinel) {
                        return node;
                    } else {
                        found = self.findBottom(node.right, true);
                    }
                // Go to the left
                } else {
                    if (node.left == &sentinel) {
                        return node;
                    } else {
                        found = self.findBottom(node.left, true);
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


            /// This function does not check if the root is red. Honestly it doesn't do any checks yet, it just returns stuff that you can check.
            /// Returns a struct contains references to two slices which point to: struct {u32, *Node} and struct {TreeError, *Node, *Node}
            fn checkValidity(self: *Self, allocator: Allocator)
            error{OutOfMemory}!struct {[]struct{u32, *Node}, []struct{TreeError, *Node, *Node}}{
                var count_list: std.ArrayList(struct {u32, *Node}) = .empty;
                var errors: std.ArrayList(struct {TreeError, *Node, *Node}) = .empty;
                errdefer count_list.deinit(allocator);
                errdefer errors.deinit(allocator);

                try self._checkValidity(allocator, self.root, &sentinel, 0, &count_list, &errors);
                return .{try count_list.toOwnedSlice(allocator), try errors.toOwnedSlice(allocator)};
            }


            /// In errors the first *Node is the current node and the second is the parent.
            fn _checkValidity(
            self: *Self,
            allocator: Allocator,
            node: *Node,
            last_node: *Node,
            count: u32,
            count_list: *std.ArrayList(struct {u32, *Node}),
            errors: *std.ArrayList(struct {TreeError, *Node, *Node}))
            error{OutOfMemory}!void{
                var new_count = count;
                if (node == &sentinel) {
                    new_count += 1;
                    try count_list.append(allocator, .{new_count, last_node});
                // double red
                } else if (node.color == Color.Red and node.parent.color == Color.Red) {
                    try errors.append(allocator, .{TreeError.double_reds, node, node.parent});
                    try self._checkValidity(allocator, node.left, node, new_count, count_list, errors);
                    try self._checkValidity(allocator, node.right, node, new_count, count_list, errors);
                // node is black
                } else if (node.color == Color.Black){
                    new_count += 1;
                    try self._checkValidity(allocator, node.left, node, new_count, count_list, errors);
                    try self._checkValidity(allocator, node.right, node, new_count, count_list, errors);
                // node is red
                } else {
                    try self._checkValidity(allocator, node.left, node, new_count, count_list, errors);
                    try self._checkValidity(allocator, node.right, node, new_count, count_list, errors);
                }
            }


            // I need to first get a list for each layer of the tree. The amount of lists is technically unbound because we have no clue how
            // many there will be. I have no clue to find out how many layers there are. You would have to create arrays on the fly. Maybe you
            // make a list/array/some storage thing that contains the lists of the layers. Then you just add another array onto it anytime
            // you need to make a new layer. We have a counter/index that determines what layer we are on and which layer/array/list we need to add to.
            // The biggest issue is making sure that all of the nodes added to a layer are in order. So we would start left and go right (or start
            // right and go left). We could do this by keeping node depth.
            fn printTree(self: *Self, allocator: Allocator) !void{
                var node = self.root;

                const Layer = std.ArrayList(*Node);
                const Layers = std.ArrayList(Layer);

                var layers: Layers = .empty;
                defer layers.deinit(allocator);
                defer for (layers.items) |layer| {
                    var temp = layer;
                    temp.deinit(allocator);
                };

                try layers.append(allocator, Layer.empty);

                var queue: std.ArrayList(*Node) = .empty;
                defer queue.deinit(allocator);

                var head: usize = 0;
                try queue.append(allocator, node);
                var length_of_layer: usize = 1;

                while (true) {
                    node = queue.items[head];
                    if (queue.items[head..].len == length_of_layer) {
                        length_of_layer *= 2;
                        try layers.append(allocator, Layer.empty);
                        try layers.items[layers.items.len - 1].appendSlice(allocator, queue.items[head..]);

                        // Check if all of the nodes are sentinels, if they are break.
                        var x: usize = 0;
                        for (layers.items[layers.items.len - 1].items) |item| {
                            if (item != &sentinel) break
                            else {
                                x += 1;
                            }
                        }
                        if (x == layers.getLast().items.len) break;
                    } // End of queue.items[head..].len == length_of_layer if statement
                    try queue.append(allocator, node.left);
                    try queue.append(allocator, node.right);
                    head += 1;
                }

                for (layers.items) |layer| {
                    for (layer.items) |n| {
                        if (n == &sentinel) {
                        std.debug.print("|{}, null|", .{n.color});
                        } else {
                        std.debug.print("|{}, {}|", .{n.color, n.data});
                        }
                    }
                    std.debug.print("line end \n", .{});
                }
            }
        };
}




// I am going to keep this commented out cause it took a decent amount of work and I think I may need something like this elsewhere.
// This all came from the printTree function before I switched to bfs.
//                const Direction = enum{
//                    left,
//                    right,
//                };
//
//                const StackData = struct{
//                    node: *Node,
//                    direction: Direction,
//                };
//
//                var stack: std.ArrayList(StackData) = .empty;
//                defer stack.deinit(allocator);
//                var count: usize = 0;
//
//                // This bit is depth first search
//                stack.append(allocator, .{node, Direction.left});
//                node = node.left;
//                count = 1;
//
//                // This while loop will visit every node, but since the tree is not perfectly symetric the amount of nodes
//                // in each layer will not be double that of the previous layer.
//                while (true) {
//                    if (node == &sentinel) {
//                        // Need to add the node to the layer it's on so that everything lines up.
//                        // Frick that will probably still miss some nodes...
//                        // I did add it in tho
//                        if (count+1 > layers.items.len) {
//                            layers.append(allocator, Layer.empty);
//                        }
//                        layers[count].append(allocator, node);
//                        stack.pop();
//                        const temp = stack.getLastOrNull();
//                        assert(temp != null);
//                        node = temp.?.node;
//                        count -= 1;
//                        continue;
//                    }
//
//                    if (count+1 > layers.items.len) {
//                        layers.append(allocator, Layer.empty);
//                        layers[count].append(allocator, node);
//
//                        stack.append(allocator, .{node, Direction.left});
//                        node = node.left;
//                        count += 1;
//                        continue;
//
//                    } else {
//                        const last = stack.getLastOrNull();
//                        assert(last != null);
//                        if (node != last.?.node) {
//                            layers[count].append(allocator, node);
//                            stack.append(allocator, .{node, Direction.left});
//
//                            node = node.left;
//                            count += 1;
//                            continue;
//                        // Last contains the the current node, this should only happen if node has been visited before
//                        } else if (last.?.direction == Direction.left) {
//                            node = node.right;
//                            last.?.direction = Direction.right;
//                            count += 1;
//                            continue;
//                        // node has been visited before and both it's left and right children have been checked
//                        } else {
//                            assert(last.?.direction == Direction.right);
//                            stack.pop();
//                            if (stack.items.len == 0) break;
//                            const temp = stack.getLastOrNull();
//                            assert(temp != null);
//                            node = temp.?.node;
//                            count -= 1;
//                        }
//                    }
//                } // End of while loop

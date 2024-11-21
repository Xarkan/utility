import typing
import json

class Tree:
    
    def __init__(self, data) -> None:
        self.data = data
        self.parent: Tree | None = None
        self.children = []


def to_set(node: Tree, set_data: set):
    if len(node.children) == 0:
        branch = upward(node)
        branch.reverse()
        set_data.add(tuple(branch))
        return
    for child in node.children:
        to_set(child,set_data)


def tree_from_dict(d, label, parent: Tree | None = None) -> Tree:
    val = ""
    if isinstance(d,typing.Hashable):
        val = d
    t = Tree(label + ":" + str(val))
    t.parent = parent
    if not isinstance(d,typing.Mapping):
        return t
    for key in d:
        child = tree_from_dict(d[key],key,t)
        t.children.append(child)
    return t


def upward(node: Tree):
    if node.parent is None:
        return [node.data]    
    return [node.data] + upward(node.parent)


def intersection(s1: set, s2: set) -> set:
    return s1 & s2


def difference(s1: set, s2: set) -> set:
    return s1 - (s1 & s2)


if __name__=="__main__":
    t1 = Tree("a")
    t2 = Tree("b")
    t3 = Tree("c")
    t4 = Tree("d")

    t1.children = [t2,t3]
    t3.parent = t1
    t2.parent = t1
    t2.children = [t4]
    t4.parent = t2

    set_data = set()
    to_set(t1,set_data)
    print(set_data)
    print("intersection:",intersection(set_data,set_data))
    print("difference:",difference(set_data,set_data))

    with open('test.json','r') as file:
        data = json.load(file)
    res = tree_from_dict(data,"root")
    set2 = set()
    to_set(res,set2)
    print(set2)
    d2 = set({('root', 'menu', 'value'), ('root', 'menu', 'popup', 'menuitem', 'value'), ('root', 'menu', 'id'), ('root', 'menu', 'popup', 'menuitem')})
    print(difference(set2,d2))


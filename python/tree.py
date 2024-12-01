import typing
import json
from typing import Optional


class TreePlaceholder:
    pass


class Tree:
    
    def __init__(self, data) -> None:
        self.data = data
        self.parent: Tree | None = None
        self.children = []


def to_set(node: Tree, set_data: set):
    if len(node.children) == 0:
        branch = _upward(node)
        branch.reverse()
        elem = tuple(branch)
        if elem in set_data:
            elem = (*elem, TreePlaceholder())
        set_data.add(elem)
        return
    for child in node.children:
        to_set(child,set_data)


def tree_from_dict(d, label, parent: Optional[Tree] = None, ordered = False) -> Tree:
    #val = ""
    t = Tree(label) # + val
    t.parent = parent
    if isinstance(d,typing.Hashable):
        #val = ":" + str(d)
        t2 = Tree(d)
        t2.parent = t
        t.children.append(t2)
        return t
    if isinstance(d,typing.Mapping):
        for key in d:
            child = tree_from_dict(d[key],key,t,ordered)
            t.children.append(child)
    elif isinstance(d, typing.List):
        for i, elem in enumerate(d):
            k = "i" if not ordered else str(i)
            child = tree_from_dict(elem,k,t,ordered)
            t.children.append(child)
    return t


def _upward(node: Tree):
    if node.parent is None:
        return [node.data]    
    return [node.data] + _upward(node.parent)


def _list_to_set(l: list):
    s = set()
    for elem in l:
        if elem in s:
            s.add((*elem, TreePlaceholder()))
            continue
        s.add(elem)
    return s


def intersection(s1: set, s2: set) -> list: 
    #return s1 & s2
    diff = difference(s1,s2)
    l = _clear_list(s1)
    for elem in diff:
        if elem in l:
            l.remove(elem)
    return l


def difference(s1: set, s2: set) -> list:
    diff1 = s1 - s2    
    diff2 = s2 - s1    
    l1 = _clear_list(diff1)
    l2 = _clear_list(diff2)
    d1 = _dict_counter(l1)
    d2 = _dict_counter(l2)
    for key in d1:
        if key in d2:
            d1[key] -= d2[key]
    res = []
    for k in d1:
        for _ in range(d1[k]):
            res.append(k)
    return res 


def _dict_counter(l: list) -> dict:
    d = {}
    for elem in l:
        if elem not in d:
            d[elem] = 1
        else:
            d[elem] += 1
    return d


def _clear_list(s: set):
    sr = [elem[:-1] if isinstance(elem[-1],TreePlaceholder) else elem for elem in s ]
    return sr

def main():
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
    #print(set_data)
    #print("intersection:",intersection(set_data,set_data))
    #print("difference:",difference(set_data,set_data))

    with open('config.json','r') as file:
        data = json.load(file)
    res = tree_from_dict(data,"root",ordered=True)
    set1 = set()
    to_set(res,set1)
    set2 = set()

    data["data"][0]["recipes"][0]["detections"]["clip_area"][1]["clip"] = 3 
    res = tree_from_dict(data,"root",ordered=True)
    to_set(res,set2)

    print(difference(set1,set2))
    d1 = set([('A','A'),('A','B'), ('A','C'),('A','C', TreePlaceholder()),('A','C', TreePlaceholder())])
    d2 = set([('A','A'),('A','B'), ('A','C'),('A','C', TreePlaceholder()),('A','D')])
    #print(intersection(d1,d2))
    print(difference(d1,d2))
    print(difference(d2,d1))
    inter = intersection(d1,d2)
    print(inter)
    print(_list_to_set(inter))


if __name__=="__main__":
    main()   

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File Name:    HashTrie.py
@Author:       icetysnow
@Mail:         liulingling05@baidu.com
@Created Time: 二, 01/05/2016, 14时33分31秒
@Copyright:    2016-2026@Baidu, Inc. All Rights Resvered.
@Description:  
"""
import sys
from collections import defaultdict

# 内部类
class _TreeNode(object):
    """存储一个节点信息"""
    def __init__(self):
        # 词性list，一个词可能有多个词性
        self.pos_list = None
        # 记录当前节点所对应的字符
        self.uchar = None
        # 记录当前节点的父亲节点
        self.father = None
        # 记录第一个子节点
        self.child = None
        # 记录右兄弟节点
        self.slibing = None

    def __str__(self):
        uchar = self.uchar
        pos_list = []
        if self.pos_list is not None:
            pos_list = self.pos_list
        return "uchar:{0}, pos_list: {1}".format(uchar.encode("utf8", "ignore"), ",".join(pos_list))

class _Word(object):
    """用于记录一个单词，debug用"""
    def __init__(self, word, pos_list):
        self.word = word
        self.pos_list = pos_list
    def __str__(self):
        return "word:{0}\tpostag:{1}".format(self.word.encode("utf8", "ignore"), ("\t".join(self.pos_list)).encode("utf8", "ignore"))


class Trie(object):
    """构建一颗字典树"""

    def __init__(self):
        # 存储每个单词所对应的节点
        self.__next = defaultdict(_TreeNode)
        # 根节点
        self.__root = _TreeNode()
        self.__root.uchar = u""
        # 迭代器记录当前遍历的状态
        # 深度优先遍历，采用栈
        t1 = (self.__root, u"")
        self.__stack = [t1]
    
    def __get_next(self, key, uchar):
        """查询next节点"""
        assert isinstance(key, unicode)
        assert isinstance(uchar, unicode)
        flag = False # flag 为true标识节点为新节点
        if key not in self.__next:
            node = _TreeNode()
            flag = True
            node.uchar = uchar
            self.__next[key] = node
        return (flag, self.__next[key])

    def insert(self, word, postag):
        """插入一个单词"""
        # word 单词（unicode）
        # postag 单词词性（unicode）
        assert isinstance(word, unicode)
        assert isinstance(postag, unicode)
        father = self.__root
        for idx, uchar in enumerate(word, 0):
            (flag, node) = self.__get_next(word[0:idx + 1], uchar)
            if flag != True:
                father = node
                continue
            # flag为True表示新节点，需要建立树状关系
            node.father = father
            if father.child is None:
                father.child = node
            else:
                node.slibing = father.child
                father.child = node
            father = node
        if father is None:
            # TODO
            sys.stderr.write("insert error: word:[0], postag:[1]".\
                    format(word.encode("utf8", "ignore"), postag("utf8", "ignore")))
            return False
        if father.pos_list is None:
            father.pos_list = [postag]
        else:
            # TODO judge duplication or not
            father.pos_list.append(postag)
        return True

    def has_word(self, word):
        """查询一个词是否在字典中，返回词性list"""
        assert isinstance(word, unicode)
        if word in self.__next:
            node = self.__next[word]
            if node.pos_list is None:
                return None
            return _Word(word, node.pos_list)
        return None

    def __iter__(self):
        """返回一个迭代器"""
        t1 = (self.__root, u"")
        self.__stack = [t1]
        return self

    def next(self):
        while len(self.__stack) != 0: 
            t = self.__stack.pop()
            (node, prefix) = (t[0], t[1])
            if node.slibing is not None:
                assert len(prefix) > 0
                t = (node.slibing, prefix[0:len(prefix) - 1] + node.slibing.uchar)
                self.__stack.append(t)
            if node.child is not None:
                t = (node.child, prefix + node.child.uchar)
                self.__stack.append(t)
            if node.pos_list is not None:
                return _Word(prefix, node.pos_list)
        raise StopIteration()
        

def trie_basic_test():
    tree = Trie()
    s1 = u"asdfadsf"
    s2 = u"aaa"
    s3 = u"bbb"
    s4 = u"aab"
    tree.insert(s1, u"ns")
    tree.insert(s2, u"nz")
    tree.insert(s3, u"v")
    tree.insert(s4, u"m")
    tree.insert(s1, u"v")
    res = tree.has_word(s1)
    if res is not None:
        print res
    res = tree.has_word(s2)
    if res is not None:
        print res
    res = tree.has_word(s3)
    if res is not None:
        print res
    res = tree.has_word(s4)
    if res is not None:
        print res
    res = tree.has_word(u"aa")
    if res is not None:
        print res
    else:
        print "aa is not a word"

    for word in tree:
        print word
        break
    for word in tree:
        print word
# trie_basic_test()

def test_feature():
    label = u"[D:None]"
    tree = Trie()
    with open("feature", "r") as fin:
        for line in fin:
            line = line.strip().decode("gbk", "ignore")
            if len(line) > 3 and line[0:3] == u"[D:":
                label = line
                continue
            tree.insert(line, label)
    for word in tree:
        print word

# test_feature()

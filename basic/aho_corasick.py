#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File Name:    aho_corasick.py
@Author:       icetysnow
@Mail:         liulingling05@baidu.com
@Created Time: 二, 01/05/2016, 17时46分24秒
@Copyright:    2016@Baidu, Inc. All Rights Resvered.
@Description:  
"""

from collections import defaultdict
import Queue
import copy

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
        # 记录失败指针
        self.fail = self
        # 记录节点的深度
        self.depth = 0

    def __str__(self):
        uchar = self.uchar
        pos_list = []
        if self.pos_list is not None:
            pos_list = self.pos_list
        return "uchar:{0}, pos_list: {1}".format(uchar.encode("utf8", "ignore"), ",".join(pos_list))

class _Word(object):
    """用于记录一个单词"""
    def __init__(self, word, pos_list):
        self.word = word
        self.pos_list = pos_list
    def __str__(self):
        return "word:{0}\tpostag:{1}".format(self.word.encode("utf8", "ignore"), ("\t".join(self.pos_list)).encode("utf8", "ignore"))


class AhoCorasick(object):
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
            node.depth = father.depth + 1
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
    
    def build_fail(self):
        """广度优先遍历构建失败指针"""
        queue = Queue.Queue()
        prefix = u""
        t = (self.__root, prefix, None)
        queue.put(t)
        while not queue.empty():
            t = queue.get()
            (node, prefix, fail_prefix) = (t[0], t[1], t[2])
            fail = node.fail
            child = node.child
            while child is not None:
                if node == self.__root:
                    child.fail = self.__root
                    tt = (child, child.uchar, u"")
                    queue.put(tt)
                else:
                    assert fail_prefix is not None
                    child_prefix = prefix + child.uchar
                    fail_child_prefix = fail_prefix + child.uchar
                    if fail_child_prefix in self.__next:
                        fail_child = self.__next[fail_child_prefix]
                        child.fail = fail_child
                    else:
                        child.fail = self.__root
                        fail_child_prefix = u""
                    tt = (child, child_prefix, fail_child_prefix)
                    queue.put(tt)
                child = child.slibing

    def __get_prefix(self, node):
        """获取单词路径"""
        prefix = u""
        while node != self.__root:
            prefix += node.uchar
            node = node.father
        return prefix[::-1]

    def get_match_word_idx(self, query):
        """查找query中包含的所有的单词位置以及词性"""
        assert isinstance(query, unicode)
        word_idx_list = []
        node = self.__root
        for idx, uchar in enumerate(query):
            uchar = query[idx]
            prefix = self.__get_prefix(node) + uchar
            while node != self.__root and prefix not in self.__next:
                node = node.fail
                prefix = self.__get_prefix(node) + uchar
            if prefix in self.__next:
                node = self.__next[prefix]
            tmp_node = node
            while tmp_node != self.__root:
                if tmp_node.pos_list is not None: # 发现一个单词
                    depth = tmp_node.depth
                    pos_list = copy.copy(tmp_node.pos_list)
                    t = (idx - depth + 1, idx + 1, pos_list)
                    word_idx_list.append(t)
                tmp_node = tmp_node.fail
        return word_idx_list

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

def basic_test():
    acto = AhoCorasick()
    acto.insert(u"ab", u"v")
    acto.insert(u"ab", u"n")
    acto.insert(u"cd", u"ns")
    acto.insert(u"fg", u"nz")
    acto.insert(u"abcdefg", u"zhuanming")
    acto.build_fail()
    for word in acto:
        print word
    word_idx_list = acto.get_match_word_idx(u"abcdefg")
    s = u"abcdefg" 
    print "seg result" 
    for ele in word_idx_list:
        word = s[ele[0]:ele[1]]
        print "word:{0} pos_tag:{1}".format(word.encode("utf8", "ignore"), (u"\t".join(ele[2])).encode("utf8", "ignore"))

# basic_test()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File Name:    raw_seg.py
@Author:       icetysnow
@Mail:         liulingling05@baidu.com
@Created Time: 三, 01/06/2016, 14时31分20秒
@Copyright:    2016@Baidu, Inc. All Rights Resvered.
@Description:  
"""

from basic.aho_corasick import AhoCorasick
import copy

class Word(object):
    """单词"""
    def __init__(self, word, pos_list):
        self.word = word
        self.pos_list = copy.copy(pos_list)

    def __str__(self):
        return "{0}|{1}".format(self.word.encode("utf8", "ignore"), (u",".join(self.pos_list)).encode("utf8", "ignore"))

class Path(object):
    """用户记录一条路径"""
    def __init__(self):
        self.word_list = []

    def __str__(self):
        return "\t".join(str(word) for word in self.word_list)

class RawSeg(object):
    """基础切词，返回多条切词路径"""

    def __init__(self):
        """初始化自动机，load词典，构建自动机"""
        self.__acto = AhoCorasick()
        with open("dict/SogouLabDic.dic", "r") as fin:
            for line in fin:
                line = line.strip()
                tokens = line.split("\t")
                if len(tokens) < 2:
                    continue
                if len(tokens) == 2:
                    word = tokens[0].decode("utf8", "ignore")
                    pos_tag = u"ProperNoun"
                    self.__acto.insert(word, pos_tag)
                elif len(tokens) == 3:
                    word = tokens[0].decode("utf8", "ignore")
                    pos_list = tokens[2].split(",")
                    sign = 0
                    for pos_tag in pos_list:
                        if len(pos_tag) == 0:
                            continue
                        sign = 1
                        pos_tag = pos_tag.decode("utf8", "ignore")
                        self.__acto.insert(word, pos_tag)
                    if sign == 0:
                        self.__acto.insert(word, u"ProperNoun")
        self.__acto.build_fail()

    def backtrace(self, ulist, N, cidx, wlist, M, widx, path_stk):
        """回溯法，寻找所有路径"""
        if cidx >= N:
            path = Path()
            path.word_list = copy.deepcopy(path_stk) 
            return [path]
        if widx >= M:
            """单词已经枚举光了"""
            path.word_list = copy.deepcopy(path_stk)
            while cidx < N:
                word = Word(ulist[cidx], [u"Single"])
                cidx += 1
                path.word_list.append(word)
            return [path]
        path_list = []
        if cidx < N:
            word = Word(ulist[cidx], [u"Single"])
            path_stk.append(word)
            path_list += self.backtrace(ulist, N, cidx + 1, wlist, M, widx, path_stk)
            path_stk.pop()
        while widx < M:
            if wlist[widx][0] < cidx:
                widx += 1
                continue
            if wlist[widx][0] > cidx:
                break
            word = Word(ulist[wlist[widx][0]:wlist[widx][1]], wlist[widx][2])
            path_stk.append(word)
            path_list += self.backtrace(ulist, N, wlist[widx][1], wlist, M, widx + 1, path_stk)
            path_stk.pop()
            widx += 1
        return path_list

    def seg(self, query):
        """对query进行切词，切分路径list"""
        assert isinstance(query, unicode)
        word_idx_list = self.__acto.get_match_word_idx(query)
        word_idx_list = sorted(word_idx_list, key=lambda x: x[0])
        path_list = []
        path_stk = []
        return self.backtrace(query, len(query), 0, word_idx_list, len(word_idx_list), 0, path_stk)
        # for ele in word_idx_list:
        #     word = query[ele[0]:ele[1]]
        #     print "word:{0} pos_tag:{1}".format(word.encode("utf8", "ignore"), (u"\t".join(ele[2])).encode("utf8", "ignore"))

segger = RawSeg()
path_list = segger.seg(u"计算机科学与技术")
for path in path_list:
    print path

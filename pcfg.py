#! /usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from utils import find_infreq_words, replace_tree, find_freq_words
from collections import defaultdict as dd


"""
COMP546 Algorithm Design and Analysis Term Project

Probabilistic Context Free Grammer Parser

"""

__author__ = "Osman Baskaya"

# Constant definitions
COUNT_FILE = 'cfg.counts'
TREE_FILE = 'parse_train.dat'
REPLACE = "_RARE_"

def gk(i, j, X):
    return "%d, %d, %s" % (i, j, X)

class PCFG(object):
    

    def __init__(self, threshold=4, tree_file=TREE_FILE, count_file=COUNT_FILE):
        """
            - threshold: denotes the infrequent words threshod (<= threshold)
            - tree_file: JSON formatted training file
            - count_file: original count file produced by using count script.

        """

        self.threshold = threshold
        self.count_file = count_file
        self.tree_file = tree_file
        #self.rules = dd(list)
        self.rules = {'unary':dd(dict), 'binary': dd(dict)}
        self.rule_counts = dd(int)


    def preprocess(self, rep_word=REPLACE):
        """
            This method provides a new file where all infrequent words replace
            with rep_word.

        """
        f = open('parse_train%d.dat' % (self.threshold + 1), 'w')
        infreq = find_infreq_words(self.threshold, self.count_file)
        newlines = replace_tree(infreq, self.tree_file, rep_word)
        f.write(''.join(newlines))
    

    def read_rules(self):
        lines = open(self.count_file).readlines()
        for line in lines:
           line = line.split()
           n = len(line)

           if n >= 4:
               count = int(line[0])
               rule = line[2] 
               param = ' '.join(line[3:])
               self.rule_counts[rule] += count
               if n == 4: # UNARY RULE
                   self.rules['unary'][rule][param] = count
               if n == 5: # Binary Rules
                   self.rules['binary'][rule][param] = count


    def estimate_param(self):
        
        """ 
            Estimates the probabilities by using MLE 
        """

        for ruletype in self.rules.keys():
            for rule in self.rules[ruletype].keys():
                for d in self.rules[ruletype][rule]:
                    self.rules[ruletype][rule][d] =  \
                        self.rules[ruletype][rule][d] / self.rule_counts[rule]

    def prepare(self, preprocess=False):
        #FIXME: else needs to be run in both cases so revise this.
        if preprocess:
            pass
        else:
            self.read_rules()
            self.estimate_param()


    def CYK(self, sentence, freq):
        sent = sentence.split()
        #sent = "What are geckos ?"
        unary = self.rules['unary']
        binary = self.rules['binary']
        #print "Untagged Sentence:", sent
        pi = dd(lambda: 0)
        bp = {}
        n = len(sent)

        for i in xrange(1, n+1):
            word = sent[i-1]
            if word not in freq:
                word = REPLACE


            p_r = [(unary[rule][word], rule, word) for \
                                    rule in unary.keys() if word in unary[rule]]
            for p, r, w in p_r:
                key = gk(i, i, r)
                pi[key] = p
                bp[key] = w, i
            
        def calc_tot(X, i, j, s):
            c = []
            for YZ in binary[X].keys():
                Y, Z = YZ.split()
                #print "pi({}, {}, {}) = q({}->{}) * pi({}) * pi({})"\
                        #.format(X, i, j, X, YZ, gk(i,s,Y), gk(s+1, j, Z))
                #print "{}, {}, {}".format(binary[X][YZ],pi[gk(i,s,Y)], pi[gk(s+1, j, Z)])
                c.append((binary[X][YZ] * pi[gk(i,s,Y)] * pi[gk(s+1, j, Z)], YZ))
            return max(c)

        for l in xrange(1, n):
            for i in xrange(1, n-l+1):
                j = i + l
                for rule in binary.keys():
                    t, r, s = max([(calc_tot(rule,i,j,s), rule, s) for s in xrange(i,j)])
                    p, YZ = t # probability and YZ tuple
                    key = gk(i,j,r)
                    pi[key] = p
                    #print pi[key], p, YZ, r, s
                    bp[key] = YZ, s

        return pi, bp

def trace(bp, root, i, j):

    key = gk(i, j, root)
    YZ, s = bp[key]
    t = YZ.split()
    l = [root,]
    if len(t) == 1:
        l.append(YZ)
    else:
        Y, Z = t
        l.append(trace(bp, Y, i, s))
        l.append(trace(bp, Z, s+1, j))
    return l


def test():
    p = PCFG(tree_file="parse_train5.dat", count_file="parse_train.counts.out")
    p.prepare()
    freq = find_freq_words(p.threshold, p.count_file)
    lines = open("parse_dev.dat").readlines()
    pi, bp = p.CYK(lines[0], freq)
    return pi, bp
    

def evaluate(dataset='test'):
    p = PCFG(tree_file="parse_train5.dat", count_file="parse_train.counts.out")
    p.prepare()
    lines = open("parse_%s.dat" % dataset).readlines()
    freq = find_freq_words(p.threshold, p.count_file)
    for sentence in lines:
        sent = sentence.split()
        last = sent[-1]
        pi, bp = p.CYK(sentence, freq)
        root = "SBARQ"
        if last != '?':
            root = "S"
        ans = trace(bp, root, 1, len(sent))
        print ans

def prep_demo():
    p = PCFG(tree_file="parse_train5.dat", count_file="parse_train.counts.out")
    p.prepare()
    freq = find_freq_words(p.threshold, p.count_file)
    return p, freq

# Demonstration
def demo(sentence):
    p, freq = prep_demo()
    sent = sentence.split()
    last = sent[-1]
    pi, bp = p.CYK(sentence, freq)
    root = "SBARQ"
    if last != '?':
        root = "S"
    ans = trace(bp, root, 1, len(sent))
    print ans
    
def main():

    
    # No need for preprocessing because we already did it.
    pcfg = PCFG(tree_file="parse_train5.dat", count_file="parse_train.counts.out")
    pcfg.prepare()
    #lines = open("parse_dev.dat").readlines()
    freq = find_freq_words(pcfg.threshold, pcfg.count_file)
    pcfg.CYK("", freq)

    #pcfg.preprocess()



if __name__ == '__main__':
    evaluate(dataset='dev')
    #main()


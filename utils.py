#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Osman Baskaya"


from collections import defaultdict as dd


def find_infreq_words(threshold, count_file):
    rule = "UNARYRULE" # this rule should be considered while finding infreq words.
    lines = open(count_file).readlines()
    d = dd(int)

    for line in lines:
        if rule in line:
            line = line.split()
            word = line[-1]
            count = int(line[0])
            d[word] += count

    return [key for key in d.keys() if d[key] <= threshold]

def find_freq_words(threshold, count_file):
    
    rule = "UNARYRULE"
    lines = open(count_file).readlines()
    infreq = find_infreq_words(threshold, count_file)
    s = set()
    for line in lines:
        if rule in line:
            line = line.split()
            word = line[-1]
            s.add(word)

    return s.difference(set(infreq))


def replace_tree(replist, tree_file, rep_word):

    """ - replist contains words to be replaced
        - rep_word is the word that infreq words replaced with it.
        - tree_file is the original tree file
    """
    
    newlines = []
    lines = open(tree_file).readlines()
    for line in lines:
        for word in replist:
            line = line.replace("\"" + word + "\"", "\"" + rep_word + "\"")

        newlines.append(line)

    return newlines
        

def main():
    infreq = find_infreq_words()
    replace_tree(infreq)
    

if __name__ == '__main__':
    main()


#-*- coding:utf-8 -*-
'''
Created on 2013-3-13

@author: Administrator
'''
import cPickle,os
from facecore import *

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR == "" : BASE_DIR = "."

C2P_FILE = BASE_DIR + "/db/c2p.db" #dictionary of chinese character to pinyin
WORD_FILE = BASE_DIR + "/prepare/words.txt" #file of words,one utf-8 word per line

def mul(B,i):
    if i == (len(B)-1):
        return B[i]
    else:
        BB = mul(B,i+1)
        result = []
        for c in B[i]:
            for x in BB:
                result.append(c+x)
        return result

def pinyin(w):
    global p2c,c2p
    buf=[ []  for i in xrange(len(w))]
    for i in xrange(len(w)):
        c = w[i]
        if c2p.has_key(c):
            for pin in c2p[c]:
                buf[i].append(pin)
            flag = True
        else:
            buf[i].append(c)
    pincodes = mul(buf,0)
    return pincodes

if __name__ == "__main__":
    print "Initializ....."
    core = FaceCore()
    p2c = cPickle.load(file(FaceCore.P2C_FILE,'rb'))
    c2p = cPickle.load(file(C2P_FILE,'rb'))
    f = open(WORD_FILE,"r")
    print "Processing...."
    while True:
        try:
            line = f.readline()
            if line=="":
                break
            line = line.strip()
            if line=="":
                continue
            word = line.decode('utf-8')
            core.addWord(word)
            if len(word)<10:
                pys = pinyin(word)
                for p in pys:
                    if p<>word:
                        core.addWord(p)
                        p2c[p.lower()] = word.lower()
        except  Exception, e:
            print e
    core.save()
    cPickle.dump(p2c,file(FaceCore.P2C_FILE,'wb'))
    print "Done."
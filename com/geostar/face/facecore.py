#-*- coding:utf-8 -*-
'''
Created on 2013-3-13

@author: Administrator
'''
import cPickle,os
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR=="" : BASE_DIR = "."

class FaceCore(object): #core of the auto complete engine
    INDEX_FILE = BASE_DIR+"/db/.index" #index file
    P2C_FILE = BASE_DIR+"/db/p2c.db"   #small dictionary of pinyin to chinese word
    MAX_WORD = 10            #max amount returned

    def __init__(self):
        if not os.path.exists(FaceCore.INDEX_FILE):
            cPickle.dump({},file(FaceCore.INDEX_FILE,"wb"))
        if not os.path.exists(FaceCore.P2C_FILE):
            cPickle.dump({},file(FaceCore.P2C_FILE,"wb"))

        self.index = cPickle.load(file(FaceCore.INDEX_FILE,"rb"))
        self.p2c = cPickle.load(file(FaceCore.P2C_FILE,"rb"))

    def addWord(self,word):
        #word must be unicode string
        d = self.index
        for w in word:
            w = w.lower()
            if d.has_key(w):
                d = d[w]
            else:
                d[w] = {}
                d = d[w]

        if d.has_key("$"):
            d['$'] = d['$']+1
        else:
            d['$'] = 1

        pass

    def glist(self,di):
        result = {}
        for k,v in di.items():
                if k == '$':
                        result[''] = v
                else:
                        child = self.glist(v)
                        for kk,vv in child.items():
                                result[k+kk] = vv
        return result

    def query(self,prefix):
        #prefix must be unicode string
        result = []
        d = self.index
        for w in prefix:
            w = w.lower()
            if d.has_key(w):
                d = d[w]
            else:
                return []

        suffixList = self.glist(d).items()
        suffixList.sort(key=lambda x:x[1],reverse=True)
        i = 0
        for su in suffixList:
            word = prefix+su[0]
            if not self.p2c.has_key(word):
                result.append(word)
            else:
                result.append(self.p2c[word])
            i +=1
            if i>FaceCore.MAX_WORD:
                break

        return list(set(result))

    def save(self):
        cPickle.dump(self.index,file(FaceCore.INDEX_FILE,"wb"))

if __name__=="__main__":
    #some unit test
    core = FaceCore()
    core.addWord(u"Jena")
    #core.save() #for persistence use
    print core.query(u"j")

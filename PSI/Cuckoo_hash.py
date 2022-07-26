import hashlib
import random
from typing import Optional, List
'''
采用一个hash函数模拟三个hash函数
number:第几个hash函数
X:要hash的字符串
n:hash表长度
'''
def Hash(number:int,X:bytes,n:int):
    cbytes=bytes(number)+X
    poshex=hashlib.md5(cbytes).hexdigest()
    pos=int(poshex,16)%n
    return pos
"""
布谷鸟hash
n: n个箱子
"""
class CuckooHash(object):
    def __init__(self,n:int,s:int):
        #初始化
        self.n=n#Hash表长度=1.2n
        self.s=s#Stash表长度=s
        self.hashtable:List[Optional[bytes]] = self.n * [None]#假设hash表中存的是bytes型,填充元素为b'00'
        self.stashtable:List[Optional[bytes]]=self.s * [None]#假设暂存区中存储的是bytes型,填充元素为b'00'
        self.StashSize=0
        self.indexset=[-1]*self.s
    def store(self,Ylist:list[bytes]):
        jump=False
        for X in Ylist:
            for i in range(100):
                #如果有空箱子
                h0=Hash(0,X,self.n)
                if self.hashtable[h0] is None:
                    self.hashtable[h0]=X
                    #记录当前元素X的存储下标
                    self.indexset[Ylist.index(X)]=h0
                    jump=True
                    break
                h1=Hash(1,X,self.n)
                if self.hashtable[h1] is None:
                    self.hashtable[h1]=X
                    self.indexset[Ylist.index(X)] = h1
                    jump=True
                    break
                h2=Hash(2,X,self.n)
                if self.hashtable[h2] is None:
                    self.hashtable[h2]=X
                    self.indexset[Ylist.index(X)] = h2
                    jump=True
                    break
                #没有空箱子,随机剔除一个元素
                selected=random.choice([h0,h1,h2])
                deleted=self.hashtable[selected]
                self.hashtable[selected]=X
                #记录下标
                self.indexset[Ylist.index(X)] = selected
                X=deleted
            if not jump:
                #存入stash表中
                self.stashtable.append(X)
                #记录下标，将box和stash视为一个标，注意下标运算
                self.indexset[Ylist.index(X)] =self.n+self.StashSize
                self.StashSize+=1
        for i in range(self.n):
            if self.hashtable[i] is None:
                self.hashtable[i]=b"00"
        for i in range(self.StashSize,self.s,1):
            self.stashtable[i]=b'00'

    @property
    def table(self) -> List[Optional[bytes]]:
        return self.hashtable
    @property
    def stash(self) -> List[Optional[bytes]]:
        return self.stashtable
    @property
    def indextable(self) -> List[Optional[int]]:
        return self.indexset










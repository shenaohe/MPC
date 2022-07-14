#减少秘密份额增长量--只讨论And门
#GESS原始方案
import random
import queue
'''
模拟 2选1 OT
select: 选择值
select bit
'''
def OT(select,selectbit):
    if selectbit:
        return select[1]
    else:
        return select[0]
'''
计算输出导线值
打表
'''
def G(x,y):
    x=str(x)
    y=str(y)
    return int(x+y,2)

sharequeue=queue.Queue(10)

#Alice执行秘密分享
def Alice(select):
    #R1,R20,R21,R3
    Rlist=[random.getrandbits(8) for i in range(4)]
    Rbinlist=[bin(_)[2:] for _ in Rlist]
    #输出导线值
    St=[G(0,0),G(0,1),G(1,0),G(1,1)]
    #b1,b20,b21,b3
    blist=[0,1,2,3]#附加标识比特
    random.shuffle(blist)
    binblist = [bin(_)[2:] for _ in blist]#打乱后的顺序
    for i in range(4):
        _=binblist[i]
        while len(_)<2:
            _='0'+_
        binblist[i]=_
    #构造第一根输入导线值
    sh10=[]
    sh11=[]
    value=[]
    for R,b in zip(Rbinlist,binblist):
        value.append(R+b)
    sh10.append(value[0])
    sh10.append(value[1])
    sh10.append(value[3])
    sh11.append(value[0])
    sh11.append(value[2])
    sh11.append(value[3])
    #构造输出导线值
    t1=random.getrandbits(2)
    t3=random.getrandbits(2)
    S=[]
    for i in range(4):
        S.append([t1,St[i],t3])
    print("the possible output is ",S)
    #构造第二条输入导线值
    sh20=[0]*4
    sh21=[0]*4
    sh20[blist[0]]=Rlist[0]^t1
    sh20[blist[1]]=Rlist[1]^St[0]
    sh20[blist[2]]=Rlist[2]^St[2]
    sh20[blist[3]]=Rlist[3]^t3
    sh21[blist[0]]=Rlist[0]^t1
    sh21[blist[1]]=Rlist[1]^St[1]
    sh21[blist[2]]=Rlist[2]^St[3]
    sh21[blist[3]]=Rlist[3]^t3
    sharequeue.put([sh20,sh21])
    #Alice输入导线值
    if select:
        return sh11
    else:
        return sh10


def Bob(select):
    Sh=sharequeue.get()
    Shb=OT(Sh,select)#10进制
    return Shb

#重建秘密值
def Recontruct(A,B):
    S=[]
    for i in range(3):
        R=int(A[i][-2:],2)
        S.append(int(A[i][:-2],2)^B[R])
    res = bin(S[1])[2:]
    while len(res)<2:
        res='0'+res
    S[1]=res
    return S
Ak=1
Bk=0
Sha=Alice(Ak)
Shb=Bob(Bk)
print("Alice input is {}".format(Ak))
print("Bob input is {}".format(Bk))
S=Recontruct(Sha,Shb)
print("--------------------------------------------------------------------")
print("the output that Alice and Bob compute is ",S)

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
    #选择随机的两个字符串R0,R1
    R0=random.getrandbits(8)#比特串一个字节
    R1=random.getrandbits(8)#比特串一个字节
    #输出导线值
    S=[G(0,0),G(0,1),G(1,0),G(1,1)]
    #构造第一条输入导线值
    b=random.getrandbits(1)#附加标识bit
    if b:
        R0bin=bin(R0)[2:]+'1'
        R1bin=bin(R1)[2:]+'0'
    else:
        R0bin=bin(R0)[2:]+'0'
        R1bin=bin(R1)[2:]+'1'
    Sh10=R0bin#字符串形式
    Sh11=R1bin
    #构造第二条输入导线值
    if b:
        Sh20 = (R1 ^ S[2],R0 ^ S[0])
        Sh21 = (R1 ^ S[3],R0 ^ S[1])
    else:
        Sh20 = (R0 ^ S[0], R1 ^ S[2])
        Sh21 = (R0 ^ S[1], R1 ^ S[3])
    sharequeue.put((Sh20,Sh21))
    #Alice输入导线值
    if select:
        return Sh11
    else:
        return Sh10

def Bob(select):
    Sh=sharequeue.get()
    Shb=OT(Sh,select)#10进制
    return Shb

#重建秘密值
def Reconstruct(A,B):
    if(A[-1]=='0'):
        re=0
    else:
        re=1
    Sha = int(A[:-1], 2)
    Shb = B[re]
    res = Sha ^ Shb
    res = bin(res)[2:]
    while len(res)<2:
        res='0'+res
    return res

Ak=1
Bk=0
Sha=Alice(Ak)
print("Alice input is {}".format(Ak))
Shb=Bob(Bk)
print("Bob input is {}".format(Bk))
S=Reconstruct(Sha,Shb)
print("the circuit output is {}".format(S))
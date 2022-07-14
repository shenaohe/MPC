#基于公钥密码学RSA的OT
from Crypto.Util.number import *
import gmpy2
# 安全参数
p=11
q=13
n=p*q
#生成公私钥对
def genpk_sk():
    phi=(p-1)*(q-1)
    pk1=getPrime(8)#公钥1
    sk1=gmpy2.invert(pk1,phi)#私钥1
    pk2=getPrime(8)#随机公钥
    return (pk1,sk1),pk2
#加密
def Enc(pk,x):
    e=pow(x<<2,pk,n)
    return e
def Dec(sk,c0,c1):
    m0=pow(c0,sk,n)
    m0bin=bin(m0)[2:]
    m1=pow(c1,sk,n)
    if m0bin[-2:]=="00":
        return m0>>2
    else:
        return m1>>2
#分享公钥,R---0或1
def getpks(R,pk0,pk1):
    if R:
        return (pk1,pk0)
    else:
        return (pk0,pk1)
#发送密文
def sendEnc(S,pks):
    e0=Enc(pks[0],S[0])
    e1=Enc(pks[1],S[1])
    return e0,e1
def OT(Sx,Rb):
    parikey,ilotkey=genpk_sk()
    pks=getpks(Rb,parikey[0],ilotkey)#Bob to Alice
    e0,e1=sendEnc(Sx,pks)#Alice to Bob
    m=Dec(parikey[1],e0,e1)#解密
    return m
print("select secret s=[5,4] with input 0 is {}".format(OT([5, 4],0)))
print("select secret s=[5,4] with input 1 is {}".format(OT([5, 4],1)))





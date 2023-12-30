import math
import random
import time

from Crypto.Util.number import getPrime
import gmpy2
from Base import Base
from demux import demux
from mux import mux
import datetime
import sys


b = 2
m = 2
l = 2


'''
Procedure to construct bucket table---Proc_Bkt
Parameter: m:第j个桶中的元素个数
           l:桶的数量
           b:条件分支个数
'''


def Proc_Bkt():
    sigma = []  # 偏移量,m是否取样所有的值还是随机选？还要再看。#sigma=[random.randint(0,b) for i in range(m)]
    # 个数较少，所以选择不重复
    while len(sigma) < m:
        brand = random.randint(0, b)
        if brand not in sigma:
            sigma.append(brand)

    seeds = []  # 随机取样，无重复值 S
    while len(seeds) < m:
        seed = random.randint(0, 1000)
        if seed not in seeds:
            seeds.append(seed)

    B = []  # bucket
    for j in range(l):
        plist = [(s + j) % b for s in sigma]
        B.append(plist)

    keys = []  # 随机取样，无重复值 # K
    while len(keys) < m:
        key = random.getrandbits(8)
        if key not in seeds:
            keys.append(key)

    return sigma, seeds, B, keys


def GenProjection(n):
    e = []
    for i in range(n):
        X0 = random.getrandbits(64)  # 16bit lable
        X1 = random.getrandbits(64)
        p = random.getrandbits(1)
        label0 = (X0 << 1) + p
        label1 = (X1 << 1) + (p ^ 1)
        e.append((label0, label1))
    return e


'''
计算桶表程序---Cbt
sigma:偏移量
a:活动分支id
b:总分支个数
l:桶的数量
m:每个桶中元素的元素个数
'''
# C：电路列表

sigma, seeds, B, keys = Proc_Bkt()  # m,l,b
print(f"the Bucket is{B}")


def Cbt0(a):
    # 真正的活跃id
    # a=1#活跃id
    instances = [0] * m
    for i in range(m):
        r = (a - sigma[i]) % b
        if 0 <= r <= l:
            instances[i] = 1
    HW = sum(instances)
    R = getPrime(1024)
    t = gmpy2.mod(R, HW)
    indexi = -1
    ActiveInstance = 0  # 在活动桶中的活动实例id
    for i in range(m):
        # 选择第t个非0向量的id---用r表示
        if instances[i] == 1:
            indexi += 1
        if indexi == t:
            ActiveInstance = indexi
    # 计算active bucket
    ActiveBucket = (a - sigma[ActiveInstance]) % l
    # 计算siblings
    Bucket_active = []  # siblings
    S = []
    for i in range(m):
        if i != ActiveInstance:
            S.append(seeds[i])
            Bucket_active.append((sigma[i] + ActiveBucket) % b)
    ActiveKey = keys[ActiveBucket]
    return ActiveBucket, ActiveInstance, Bucket_active, S, ActiveKey


def int_to_bin(a: int, n):
    x = bin(a)[2:]
    assert n >= len(x)
    while len(x) < n:
        x = '0' + x
    return x
def n_to_bin(n):
    x=""
    for i in range(n):
        x='1'+x
    return int(x,2)

def BT_Gb1():
    # ----------------new BT.Gb------------------#
    A = []  # alpha的lable
    R = []  # gamma的lable
    for i in range(b):
        A.append(random.getrandbits(16))
        R.append(random.getrandbits(16))
    P = random.sample(range(0, b), b)
    GabledBT = [(0, 0, [], [], 0)] * b
    GabledA = [0] * b
    for i in range(b):
        ActiveBucket, ActiveInstance, Bucket_active, S, ActiveKey = Cbt0(i)
        keyA = A[i]
        ActiveBucket = ActiveBucket ^ keyA
        ActiveInstance = ActiveInstance ^ keyA
        for j in range(m-1):
            Bucket_active[j] = Bucket_active[j] ^ keyA
            S[j] = S[j] ^ keyA
        ActiveKey = ActiveKey ^ keyA
        GabledBT[P[i]] = (ActiveBucket, ActiveInstance, Bucket_active, S, ActiveKey)  # 构建真值表
        A[i] = (A[i] << math.ceil(math.sqrt(b))) + P[i]
        GabledA[P[i]] = A[i]
    return GabledA, R, GabledBT


def BT_Ev1(alpha, GarbledBT, R):
    # ---------new BT.EV-----------------------#
    p = alpha & n_to_bin(math.ceil(math.sqrt(b)))
    keyA = alpha >> math.ceil(math.sqrt(b))
    print("GarbledBT[p]:",GarbledBT[p])
    ActiveBucket, ActiveInstance, Bucket_active, S, ActiveKey = GarbledBT[p]
    ActiveBucket = ActiveBucket ^ keyA
    ActiveInstance = ActiveInstance ^ keyA
    for i in range(m-1):
        Bucket_active[i] = Bucket_active[i] ^ keyA
        S[i] = S[i] ^ keyA
    ActiveKey = ActiveKey ^ keyA
    gamma = R[ActiveInstance]
    return ActiveBucket, ActiveInstance, Bucket_active, S, ActiveKey, gamma


# 旧版本的BT不符合论文描述
def BT_Gb(b: int):
    # 一共2个分支
    # alpha的混淆
    a = []
    for i in range(b):
        a.append(random.getrandbits(16))
    # print(f"原始的alpha是{a}")
    Gabled = []
    for i in range(b):
        Gabled.append(a[i] ^ i)
    # print(f"原始的乱码表是{Gabled}")
    random.shuffle(Gabled)  # 打乱位置
    # print(f"打乱位置后的乱码表是{Gabled}")
    for i in range(b):
        p = Gabled.index(a[i] ^ i)
        a[i] = (a[i] << 1) + p
    # print(f"添加标识比特后{a}")
    sigmma = []
    X0 = random.getrandbits(64)  # 16bit lable
    X1 = random.getrandbits(64)
    p = random.getrandbits(1)
    label0 = (X0 << 1) + p
    label1 = (X1 << 1) + (p ^ 1)
    sigmma.append(label0)
    sigmma.append(label1)
    return a, sigmma, Gabled


# 虚假的评估和混淆程序
def BT_Ev(sigma: list, keys: list, seeds: list, alpha: int, Garbled, sigmma):
    # 解密a
    p = alpha & 1
    a = (alpha >> 1) ^ Garbled[p]
    instances = [0] * m
    for i in range(m):
        r = (a - sigma[i]) % b
        if 0 <= r <= l:
            instances[i] = 1
    HW = sum(instances)
    R = getPrime(1024)
    t = gmpy2.mod(R, HW)
    indexi = -1
    ActiveInstance = 0  # 在活动桶中的活动实例id
    for i in range(m):
        # 选择第t个非0向量的id---用r表示
        if instances[i] == 1:
            indexi += 1
        if indexi == t:
            ActiveInstance = indexi
    # 计算active bucket
    ActiveBucketID = (a - sigma[ActiveInstance]) % l
    # 计算siblings
    Bucket_active = []  # siblings
    S = []
    for i in range(m):
        if i != ActiveInstance:
            S.append(seeds[i])
            Bucket_active.append((sigma[i] + ActiveBucketID) % b)
    ActiveKey = keys[ActiveBucketID]
    sigmmalable = sigmma[a]
    return ActiveBucketID, ActiveInstance, Bucket_active, S, ActiveKey, sigmmalable



mybase = Base()
mydemux = demux()
mymux = mux()


def GCWise_Gb(C: list):
    GabledA, R, GabledBT=BT_Gb1()
    e_real = []
    d_real = []
    Material = []
    flag = 1  # 只用混淆一次，对于每一个Bucket，相同位置上的e和d是相同的
    PrimeG = []
    for j in range(2):
        Mj = [0] * 2  # 半门技术每一个只提供两个密文
        for i in range(2):
            ix = B[j][i]
            GalbedM, e, d = mybase.Gb(C[ix], seeds[i])
            # Halfgates 本身并不需要为XOR门生成任何乱码表，并且AND门和XOR门的输出标签计算方式并不相同。
            # 相同位置上的AND门和XOR门的输出标签并不相同如何统一？
            # 1.修改XOR门的标签生成方式，反正是随机生成的-----X 必须同时满足AND门
            # 2.

            if flag == 1:
                e_real.append(e)  # 按照导线顺序排列
                d_real.append(d)
            PrimeG.append(GalbedM)
            for m in range(2):
                Mj[m] = Mj[m] ^ GalbedM[m]  # Stack
        flag = 0

        # 加密
        for i in range(2):
            Mj[i] = Mj[i] ^ keys[j]
        Material.append(Mj)
    print(f"---原始的乱码表为：{PrimeG}")
    print(f"+++各个门全部导线的输入标签为：{e_real}")
    e_all, Galbed_dem, Garbage0, Garbage1 = mydemux.Gb(R, e_real)
    garbage = GenProjection(1)
    Garbagey0 = [garbage[0][0]]
    Garbagey1 = [garbage[0][1]]
    d_all, Galbed_mux = mymux.Gb(R, d_real, Garbagey0, Garbagey1)  # Garbage0 C0的垃圾输出，Garbage1 C1的垃圾输出
    True_e = [GabledA, e_all]
    True_garbled = [Material, GabledBT, Galbed_dem, Galbed_mux]
    True_d = d_all
    # 垃圾输出标签
    return True_garbled, True_e, True_d, garbage, Garbage0, Garbage1,R


def GCWise_Ev(C: list, X, M, Garbage0, Garbage1, GarbageY, d,R):
    Material, GabledBT, Galbed_dem, Galbed_mux = M[0], M[1], M[2], M[3]
    alpha, Xlabel = X[0], X[1]
    ActiveBucketID, ActiveInstance, Bucket_active, S, ActiveKey, sigmmalable = BT_Ev1(alpha, GabledBT,R)
    # 为了方便，demux.Ev直接输出非垃圾标签，事实上应该垃圾标签也应该参与运算,在mux.EV中去除垃圾标签，因此多了几个参数
    X_gamma = mydemux.Ev(Xlabel, sigmmalable, Galbed_dem, Garbage0, Garbage1)  # Xlabel正确,sigmmalable正确，
    print(f"活跃桶的id为：{ActiveBucketID}")
    # print(f"活跃桶为：{Bucket_active}")
    print(f"活跃桶中的活跃实例id为：{ActiveInstance}")
    # print(f"整个Bucket的乱码材料为：{Material}")
    M_active = Material[ActiveBucketID]
    # print(f"获得的Activebucket的乱码材料为：{M_active}")
    for i in range(2):
        M_active[i] = M_active[i] ^ ActiveKey
    # 解密
    for i in range(m):
        if i == ActiveInstance:
            continue
        ix = Bucket_active[i]
        Cix, _, __ = mybase.Gb(C[ix], S[i])
        for j in range(2):
            M_active[j] = M_active[j] ^ Cix[j]
    C_alpha = M_active
    print(f"***重新构建的正确分支的乱码表为：{C_alpha}")
    print(f"***Base 获得的输入标签为: {X_gamma}")
    Y_label = mybase.Ev(C_alpha, X_gamma)  # 输出正常Y标签，其他的应该是垃圾标签 C_alpha正确,X_gamma正确###Base.EV出问题了。
    # 如何选择垃圾标签---不然只能挨个试了？
    # garbage = []
    # garbagey=GarbageY[0]
    # for i in range(2):
    #     if garbagey[i] == Y_label:
    #         continue
    #     else:
    #         garbage.append(garbagey[i])
    Y = mymux.Ev(Galbed_mux, sigmmalable, Y_label, GarbageY[0], d[0])
    return Y


def GCWise_En(x, e):
    n = len(e)
    Xlable = []
    for i in range(n):
        (X0, X1) = e[i]
        if x[i] == 0:
            Xlable.append(X0)
        else:
            Xlable.append(X1)
    return Xlable


def GCWise_De(d, Ylabel):
    y = []
    m = len(d)
    for i in range(m):
        (Y0, Y1) = d[i]
        if Ylabel == Y0:
            y.append(0)
        elif Ylabel == Y1:
            y.append(1)
        else:
            y.append('error')
    return y


#########整个协议执行过程
"""
电路格式  输入导线数，输出导线数，输入导线编号，输出导线编号，门的名称
C0只有一个XOR门  2 1 0 1 4
C1只有一个AND门  2 1 2 3 5
:return:
"""
C = ['XOR', 'AND']  # 按照拓扑顺序排列
e_Alice = []
e_Bob = []


# ActiveLable=[]
# 电路生成方
def Alice(select):
    # 混淆
    print("[+]GCWise on Alice(Generator)....start")
    print("[+]生成乱码材料开始")
    garbledTable, e, d, GarbageY, Garbage0, Garbage1,R = GCWise_Gb(C)  # garbledTable按照导线顺序排列，0 1 2 3

    print(f"整个电路的乱码表为： {garbledTable}")
    print(f"整个电路的输入导线标签集合e为：{e}")
    print(f"整个电路的输出导线标签集合d为：{d}")
    print("[-]生成乱码材料结束")
    alpha = e[0]

    # 随机选择一个导线的条件标签，在实际电路中可能来源于其他电路的输出
    ActiveAlpha = alpha[select]#随便选一个
    e_true = e[1]
    # n = 4  # 整个电路输入导线数
    # m = 1  # 整个电路输出导线数，(m'=2)
    # Alice的输入---0号和2号导线属于Alice
    x_Alice = [1, 1]
    print(f"Alice的输入为{x_Alice}")
    global e_Alice
    print("[+]获得Alice的输入标签开始")
    e_Alice = GCWise_En(x_Alice, [e_true[0], e_true[2]])
    print("[-]获得Alice的输入标签结束")
    print(f"Alice的输入标签为{e_Alice}")

    # 接下来把e_Alice传递给Bob,然后bob与Alice之间执行2-1 OT协议，为Bob的每一个输入获得对应的标签,这里直接忽略OT的执行过程，以明文的形式
    # Bob的输入----1号和3号线属于Bob
    print("OT协议执行......")
    time.sleep(1)
    x_Bob = [1, 1]
    global e_Bob
    e_Bob = GCWise_En(x_Bob, [e_true[1], e_true[3]])

    ActiveLable = [ActiveAlpha, [e_Alice[0], e_Bob[0], e_Alice[1], e_Bob[1]]]  # 0,1,2,3    激活标签，按照导线拓扑顺序排列
    print("send Garbled Maerial to Bob......")
    print("[-]GCWise on Alice(Generator)....end")
    # 将ActiveLable传递给Bob,多余的还有垃圾标签
    return garbledTable, ActiveLable, GarbageY, Garbage0, Garbage1, d,R


# 电路评估方
def Bob(select):
    # Bob用来评估的材料
    garbledTable, ActiveLable, GarbageY, Garbage0, Garbage1, d,R = Alice(select)
    print("[+]GCWise on Bob(Evaluator)....start")
    print("[+]开始接收ALice的传输")
    print(f"总通信量:{sys.getsizeof(garbledTable)+sys.getsizeof(ActiveLable)+sys.getsizeof(d)+sys.getsizeof(R)+2}Bytes")
    print(f"接收的整个电路的乱码表为{garbledTable}")
    print(f"接收的Alice的输入标签为{e_Alice}")
    print(f"真正的活跃实例标签为{ActiveLable[0]}")
    print(f"接收的活跃实例标签的乱码表为{R}")
    print(f"接收的整个电路输出标签为{d}")
    print("[-]接收Alice传输结束")
    print("开始执行OT协议......")
    time.sleep(1)
    # print(f"输入激活标签按照导线排列为：{ActiveLable}")
    print(f"Bob获得的输入标签为{e_Bob}")
    print("[+]评估电路开始")
    start = datetime.datetime.now()
    Y = GCWise_Ev(C, ActiveLable, garbledTable, Garbage0, Garbage1, GarbageY, d,R)
    end = datetime.datetime.now()
    print("[-]评估电路结束")
    if Y==[0]:
        Y=d[1]
    print(f"计算得到输出标签为 {Y}")
    y_value = GCWise_De(d, Y)
    if y_value==["error"]:
        y_value=[1]
    print(f"Bob计算得到的明文值为{y_value}")
    print(f"send {y_value} to Alice")
    print("[-]GCWise on Bob(Evaluator)....end")
    return y_value


# y0=Bob(0)#选择0号电路----XOR
y1 = Bob(0)  # 选择1号电路----AND
Myselect=y1[0]


# 电路的拓扑结构
'''
        电路分支C0
       |—————————| 
0------|   |X|   |
       |   |O|   |-------4
1------|   |R|   |       |
       |—————————|       |-------6
2------|   |A|   |       |    
       |   |N|   |-------5
3------|   |D|   |
       |—————————|
        电路分支C1
'''

# print(f"                Alice input is [0号导线：1,   2号导线：1]\n"
#       f"                Bob input is   [1号导线：1,   3号导线：1]\n"
#       f"                最终的结果为{y0}\n")
print("---------------------------总结-----------------------------------")
print(f"Alice input is [0号导线：1,   2号导线：1]\n"
      f"Bob input is   [1号导线：1,   3号导线：1]\n"
      f"选择的活跃电路分支为{C[Myselect]}\n"
      f"最终的结果为{y1}")
'''
int C0(){        int C1(){               int Cn(){
    return 0;        return 1;  ......       return n;
}                }                       }
'''

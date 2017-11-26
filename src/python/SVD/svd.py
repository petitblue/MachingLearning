#coding:utf-8

'''
时间: 2017/11/26
作者: BigNewbie
参考文献: [机器学习笔记]奇异值分解SVD简介及其在推荐系统中的简单应用 https://www.cnblogs.com/lzllovesyl/p/5243370.html
            【机器学习实战】第14章 利用SVD简化数据 http://www.cnblogs.com/jiangzhonglian/p/7815289.html
实现算法 SVD
实现功能 基于SVD的相似物品推荐系统
         基于SVD的图像压缩功能示例
'''
print(__doc__)

import numpy as np
import numpy.linalg as la


def loadExData3():
    # 利用SVD提高推荐效果，菜肴矩阵
    return[[2, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
           [0, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0],
           [3, 3, 4, 0, 3, 0, 0, 2, 2, 0, 0],
           [5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0],
           [4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 5],
           [0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 4],
           [0, 0, 0, 0, 0, 0, 5, 0, 0, 5, 0],
           [0, 0, 0, 3, 0, 0, 0, 0, 4, 5, 0],
           [1, 1, 2, 1, 1, 2, 1, 0, 4, 5, 0]]


# 相似度计算,将所有相似度结果约束到[0,1]之间。inA, inB为列向量


# 基于欧氏距离求解相似度
def ecludSim(inA, inB):
    return 1.0/(1.0 + la.norm(inA-inB))

# 基于皮尔逊相关系数计算相似度
def pearsSim(inA, inB):
    return 0.5 + 0.5 * np.corrcoef(inA, inB, rowvar=0)[0][1]

# 基于余弦值计算相似度
def cosSim(inA, inB):
    cos = float(inA.T*intB)/(la.norm(inA)*la.norm(inB))
    return 0.5 + 0.5*cos

# 基于非SVD计算两物品相似度给未打分item打分
def standEst(dataMat, user, simMeas, item):
    """standEst(计算用户未评价商品item的期望打分，通过计算item和用户user打过分的商品的相似度计算item评分，相似度使用simMeas方法(欧氏、皮尔逊系数、余弦相似度三选一))

    Args:
        dataMat 用户评分数据集。行表示用户，列表示商品菜单
        user 要估算商品的用户，用行号表示
        simMeas 相似度计算方法，有欧式、皮尔逊系数、余弦相似度三种
        item 用户user未评价商品号，用列号表示

    Return:
        ratSimTotal/simTotal 评分(0~5之间)
    """

    # 获取物品数目
    n = np.shape(dataMat)[1]
    ratSimTotal = 0.0
    simTotal = 0.0

    for i in range(n):
        userRating = dataMat[user, i]
        # 如果用户评分为0，跳过
        if userRating == 0:
            continue

        overlapInd = np.nonzero(np.logical_and(dataMat[:, i]>0, dataMat[:, item]>0))[0]
        if len(overlapInd) == 0:
            similarity = 0
        else:
            similarity =  simMeas(dataMat[overlapInd, i], dataMat[overlapInd, item])

        # 计算总相似度
        simTotal += similarity
        # 计算评分总相似度
        ratSimTotal += similarity * userRating

    """
    ratSimTotal/simTotal含义: ratSimTotal/simTotal = (rate1*sim1 + rate2*sim2+...+rateN*simN) / (sim1+sim2+sim3+...+simN) = rate1 * P1 + rate2 * P2 + ... + rateN*PN
    其中PN表示第N个商品和item相似度占整个相似度的百分比，式子的结果是打分在相似度下的数学期望
    """
    if simTotal == 0:
        return 0
    else:
        return ratSimTotal / simTotal


# 基于SVD计算两物品相似度给未打分item打分
def svdEst(dataMat, user, simMeas, item):
    """svdEst(使用基于SVD降维方法计算两物品相似度。和传统standEst相比，将MxN矩阵分解为u(MxM),sig(MxN),vT(NxN)三个矩阵,
              将数据降到k维变为u(M*k) * np.diag(s)(k*k) * vT(k*N))

    Args:
        同standEst
    Return:
        同上
    """
    n = np.shape(dataMat)[1]
    ratSimTotal = 0.0
    simTottal = 0.0

    # 计算svd
    k = 4
    u, sigma, v = la.svd(dataMat)
    sigK = np.eye(k)*sigma[:k]
    transformItemsV = dataMat.T * u[:,:k] * sigk.I

    print("dataMat", np.shape(dataMat))
    print("u", np.shape(u[:,k]))
    print("sigk", np.shape(sigk))
    print("v", np.shape(v[:k,:]))
    print("transformItemsV", np.shape(transformItemsV))

    for i in range(n):
        userRating = dataMat[user, i]
        if userRating==0:
            continue

        # 基于SVD降维的数据求解相似度
        similarity = simMeas(transformItemsV[item, :].T, transformItemsV[i, :].T)

        # 求解总相似度和总评分
        simTotal += similarity
        ratSimTotal += userRating * similarity

    if simTotal ==0:
        return 0
    else:
        return ratSimTotal/simTotal

# 推荐系统
def recommand(dataMat, user, topNItems=3, simMeas=cosSim, estMethod=standEst):
    """recommand(给用户推荐前topNItem未打分商品，默认为3)

    Args:
        dataMat 用户数据
        user 用户
        topNItems 打分靠前的N商品
        simMeas 相似度估计方法，默认使用cosSim
        estMethod 打分策略,默认使用标准估计方法

    Returns:
        返回N个推荐商品

    """
    unRatedItems = np.nonzero(dataMat[user,:]==0)[1]
    if len(unRatedItems):
        return "You rated everything"

    itemScores = []
    for item in unRatedItems:
        rateScore = estMethod(dataMat, user, simMeas, item)
        itemScores.append((item, rateScore))

    return sorted(itemScore, key=lambda x:x[1], reversed=True)[:topNItems]

def analyse_data(Sigma, Num=20):
    """analyse_data(分析Sigma的取值个数，默认为20)

    Args:
        Sigma Sigma值
        Num 要判断的个数
    """

    Sigma2 = Sigma**2
    SigmaSum = float(np.sum(Sigma2))
    sigmaTotal = 0.0
    Num = min(len(Sigma2), NUM)
    for i in range(Num):
        sigmaTotal += Sigma2[i]
        print("主成分:%d, 方差占比:%.2f"%(i+1, sigmaTotal*100/sigmaSum))

# 图像压缩

# 读取图像
def loadImgData(filename):
    return np.mat([[int(line[i]) for i in range(32)] for line in open(filename).readlines()])

# 打印图像
def printImgData(imgMat, threshold):
    for i in range(32):
        for j in range(32):
            if float(imgMat[i,j])>threshold:
                print 1,
            else
                print 0,
            print ''

# 图像压缩重构
def imgCompress(numSVD=3, thresh=0.8):
    """ImgCompress(图像压缩，借助SVD将图像压缩后重新构建)

    Args:
        numSVD 降维后维度
        trhresh 图像阈值
    """
    imgMat = loadImagData('../../../data/SVD/0.txt')
    printImgMat(imgMat, thresh)

    u,Sigma,v = la.svd(imgMat)

    analysis_data(Sigma, 20)

    SigReco = np.eye(numSVD)*Sigma[:numSVD]
    reconMat = u[:, :numSVD] * SigReco * v[:numSVD,:]
    printImgMat(reconMat, thresh)

def main():

    dataMat = loadExData3()
    recItems1 = recommand(dataMat, user=0, topNItems=3, simMeas=cosSim, estMethod=standEst)
    recItems2 = recommand(dataMat, user=0, topNItems=3, simMeas=EucldSim, estMethod=standEst)
    recItems3 = recommand(dataMat, user=0, topNItems=3, simMeas=PersSim, estMethod=standEst)

    recItems4 = recommand(dataMat, user=1, topNItems=3, simMeas=cosSim, estMethod=svdEst)
    recItems5 = recommand(dataMat, user=1, topNItems=3, simMeas=EucldSim, estMethod=svdEst)
    recItems6 = recommand(dataMat, user=1, topNItems=3, simMeas=PersinSim, estMethod=svdEst)

    print(recItem1)
    print(recItem2)
    print(recItem3)
    print(recItem4)
    print(recItem5)
    print(recItem6)

    imgCompress(numSVD=3， thresh=0.8)







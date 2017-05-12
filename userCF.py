# -*-coding:utf-8-*-

from math import sqrt
import random

random.seed(0)
class UserBasedCF:

    def __init__(self):
        self.trainset_len = 0
        self.sim_mat = {}
        self.train = {}

    @staticmethod
    def loadBase():
        ''' load file from dataBase, return a generator. '''
        fp = open('movieTest.csv','r')
        for i, line in enumerate(fp):
            yield line
            if i % 100000 == 0:
                print('loading (%s)' % i)
        print('load database succ')

    def generate_dataset(self, pivot=0.3):
        ''' load rating data and split it to training set and test set '''
        trainset_len = 0

        for line in self.loadBase():
            user, movie, rating = line.split(',')
            # split the data by pivot
            self.train.setdefault(user, {})
            self.train[user][movie] = float(rating)
            trainset_len += 1

        print('split training set and test set succ')
        print('train set = %s' % trainset_len)

    def sim_distance(self, p1, p2):
        '欧几里得距离计算相似度'
        si = {}
        for item in self.train[p1]:
            if item in self.train[p2]:
                si[item] = 1

        if len(si) == 0: return 0

        sum_of_squares = sum([pow(self.train[p1][item] - self.train[p2][item], 2)
                              for item in self.train[p1] if item in self.train[p2]])

        return 1 / (1 + sqrt(sum_of_squares))

    def sim_pearson(self, p1, p2):
        'pearson相似系数计算相似度'
        si = {}
        for item in self.train[p1]:
            if item in self.train[p2]:
                si[item] = 1

        n = len(si)

        if n == 0: return 0

        sum1 = sum([self.train[p1][item] for item in si])
        sum2 = sum([self.train[p2][item] for item in si])

        sum1Sq = sum([pow(self.train[p1][item], 2) for item in si])
        sum2Sq = sum([pow(self.train[p2][item], 2) for item in si])

        pSum = sum([self.train[p1][item] * self.train[p2][item] for item in si])

        num = pSum - (sum1 * sum2 / n)
        den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
        if den == 0: return 0
        r = num / den
        return r

    def cal_user_sim(self, person):
        sim_martix = {}
        count = 0
        for p2 in self.train.keys():
            if person == p2:
                continue
            sim = self.sim_distance(person, p2)
            sim_martix.setdefault(person, {})
            sim_martix[person].setdefault(p2, sim)
            count += 1
            if (count % 10000 == 0):
                print('共进行了%d次pearson计算' % count)
        self.sim_mat = sim_martix
        print('computer sim_mat is done!')

    def recommend(self, person):
        '默认为使用pearson计算相似度'
        K=20
        N=10
        if person not in self.train.keys():
            return None
        rank = {}
        sim_sum = {}
        #rank[it]代表的是相似度和评分成绩之和，
        #sim_sum[it]是对it的评过分的相似度之和
        for person2, sim_person in sorted(list(self.sim_mat[person].items()), key=lambda s: s[1], reverse=True)[:K]:
            # p1和p2的相似度乘以p2对it1的评分
            for it,rating in self.train[person2].items():
                if it in self.train[person]:
                    continue
                rank.setdefault(it,0)
                sim_sum.setdefault(it,0)
                sim_sum[it] += sim_person
                rank[it] += sim_person * rating
        rank = [(item,weight/sim_sum[item]) for item,weight in rank.items()]
        # 消除误差
        return sorted(rank, key=lambda s: s[1], reverse=True)[:N]

# 声明一个ItemBased推荐的  对象
usercf = UserBasedCF()
usercf.generate_dataset()
usercf.cal_user_sim('A')
for rank_result in usercf.recommend('A'):
    print('推荐%s，推荐度%.2f' %(rank_result[0],rank_result[1]))


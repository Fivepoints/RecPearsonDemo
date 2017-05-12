# -*-coding:utf-8-*-

from math import sqrt
import random

random.seed(0)
class ItemBasedCF:

    def __init__(self):
        self.trainset_len = 0
        self.sim_mat = {}
        self.train = {}
        self.item_users = {}

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

            # if (random.random() < pivot):
            #     self.trainset.setdefault(user,{})
            #     self.trainset[user][movie] = float(rating)
            #     trainset_len += 1
            # else:
            #     self.testset.setdefault(user,{})
            #     self.testset[user][movie] = float(rating)
            #     testset_len += 1

        print('split training set and test set succ')
        print('train set = %s' % trainset_len)
        # print('test set = %s' % testset_len, file=sys.stderr)

    def sim_distance(self, it1, it2):
        '欧几里得距离计算相似度'
        si = {}
        for user in self.item_users[it1]:
            if user in self.item_users[it2]:
                si[user] = 1

        if len(si) == 0: return 0

        sum_of_squares = sum([pow(self.item_users[it1][user] - self.item_users[it2][user], 2)
                              for user in self.item_users[it1] if user in self.item_users[it2]])

        return 1 / (1 + sqrt(sum_of_squares))

    def sim_pearson(self, it1, it2):
        'pearson相似系数计算相似度'
        si = {}
        for user in self.item_users[it1]:
            if user in self.item_users[it2]:
                si[user] = 1

        n = len(si)

        if n == 0: return 0

        sum1 = sum([self.item_users[it1][user] for user in si])
        sum2 = sum([self.item_users[it2][user] for user in si])

        sum1Sq = sum([pow(self.item_users[it1][user], 2) for user in si])
        sum2Sq = sum([pow(self.item_users[it2][user], 2) for user in si])

        pSum = sum([self.item_users[it1][user] * self.item_users[it2][user] for user in si])

        num = pSum - (sum1 * sum2 / n)
        den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
        if den == 0: return 0
        r = num / den
        return r

    def transformPrefs(self):
        result = {}
        for person in self.train:
            for item in self.train[person]:
                result.setdefault(item, {})
                result[item][person] = self.train[person][item]
        self.item_users = result


    def cal_user_sim(self, person):
        '对于基于物品的推荐要加一个物品－用户的逆矩阵操作'
        self.transformPrefs()
        sim_martix = {}
        count = 0
        for it1 in self.train[person].keys():
            for it2 in self.item_users.keys():
                if it1 == it2:
                    continue
                else:
                    sim = self.sim_pearson(it1, it2)
                    sim_martix.setdefault(it1, {})
                    sim_martix[it1].setdefault(it2, sim)
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
        for it1, rating in self.train[person].items():
            for it2, sim_it1 in sorted(list(self.sim_mat[it1].items()), key=lambda s: s[1], reverse=True)[:K]:
                # it1和it2的相似度乘以用户对it1的评分
                if it2 in self.train[person]:
                    continue
                rank.setdefault(it2,0)
                rank[it2] += sim_it1 * rating
        rank = [(item, weight / 1) for item, weight in rank.items()]
        return sorted(rank, key=lambda s: s[1], reverse=True)[:N]

# 声明一个ItemBased推荐的对象
itemcf = ItemBasedCF()
itemcf.generate_dataset()
itemcf.cal_user_sim('A')
for rank_result in itemcf.recommend('A'):
    print('推荐%s，推荐指数%.2f' %(rank_result[0],rank_result[1]))


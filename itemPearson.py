# -*-coding:utf-8-*-

from math import sqrt
import random

random.seed(0)
class ItemBasedCF:

    def __init__(self, train_file):
        self.trainset_len = 0
        self.sim_mat = {}
        self.train_file = train_file
        self.readData()

    def readData(self, pivot=0.3):
        # 读取文件，并生成用户-物品的评分表和测试集
        self.train = dict()  # 用户-物品的评分表
        for line in open(self.train_file):
            user,item,score = line.strip().split(",")[:3]
            self.train.setdefault(user, {})
            self.train[user][item] = float(score)
            self.trainset_len += 1


        print('加载数据集完成,共加载%d' %self.trainset_len)

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

        if n == 0: return 1

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
    def cal_user_sim(self,person):
        sim_mat = self.sim_mat
        count = 0
        for it1 in self.train[person].keys():
            for it2 in self.item_users:
                if it1 == it2:
                    continue
                else:
                    sim = self.sim_pearson(it1, it2)
                    sim_mat.setdefault(it1, {})
                    sim_mat[it1].setdefault(it2, sim)
                    count += 1
                    if (count % 10000 == 0):
                        print('共进行了%d次pearson计算' % count)
    def getRcommendations(self,person):
        '默认为使用pearson计算相似度'
        K=20
        N=10
        sim_mat = self.sim_mat
        rank = {}
        for it1, rating in self.train[person].items():
            for it2, sim_it1 in sorted(list(sim_mat[it1].items()), key=lambda s: s[1], reverse=True)[:N]:
                # it1和it2的相似度乘以用户对it1的评分
                if it2 in self.train[person]:
                    continue
                rank.setdefault(it2,{})
                rank[it2].setdefault('weight', 0)
                rank[it2].setdefault('reason', {})
                rank[it2]['weight'] += sim_mat[it1][it2] * rating
                rank[it2]['reason'].setdefault(it1,0)
                rank[it2]['reason'][it1] = sim_mat[it1][it2] * rating
                print('%s 和　%s 的相似度是%.2f' %(it1,it2,float(sim_mat[it1][it2])))

        return sorted(list(rank.items()), key=lambda s: s[1]['weight'], reverse=True)[:N]
        # for other in self.train.keys():
        #     # 排除自己
        #     if other == person: continue
        #     sim = self.sim_pearson(person, other)
        #     count += 1
        #     # 排除相似度<0情况
        #     if sim <= 0: continue
        #     for item in self.train[other]:
        #         # 排除看过的
        #         if item not in self.train[person] or self.train[person][item] == 0:
        #             # 相似度*评价 之和
        #             totals.setdefault(item, 0)
        #             totals[item] += self.train[other][item] * sim
        #             # 相似度之和
        #             simSums.setdefault(item, 0)
        #             simSums[item] += sim
        #
        # rankings = [(total / simSums[item], item) for item, total in totals.items()]
        # # 排序并调转
        # rankings.sort()
        # rankings.reverse()
        # print('共进行了%d次pearson计算' %count)
        # return rankings[:10]

# 声明一个ItemBased推荐的对象
item = ItemBasedCF("movieTest.csv")
item.transformPrefs()
item.cal_user_sim('A')
print(item.getRcommendations('A'))

# Item.ItemSimilarity()
# recommedDic = Item.Recommend('1')
# print(recommedDic)
# for k, v in recommedDic.iteritems():
#     print(k, "　", v)
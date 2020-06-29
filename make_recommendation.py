# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 19:55:58 2019
@author: 
"""

import json
from math import sqrt
import pymysql as db
'''
    加载数据库中的数据，并转换为json格式
'''
# 连接数据库
connect = db.Connect(
    host='localhost',
    port=3306,
    user='root',
    passwd='root',
    db='django',
    charset='utf8mb4'
)
# 获取游标
cursor = connect.cursor()
cursor.execute("SELECT * FROM s_useraction")
date_set = cursor.fetchall()
json_date = {}
for date in date_set:
    json_date.setdefault(date[4], {})
    json_date[date[4]].setdefault("movies", {})
    json_date[date[4]]["movies"].setdefault(date[1], {})
    json_date[date[4]]["movies"][date[1]]["movie_rate"] = date[2]
movie_data = json_date
# 这里填你豆瓣的id
my_name = "炎樱"
# file = open('movie_data.json', 'r', encoding='utf-8')
# movie_data = json.load(file)
# file.close()

'''
    协同过滤推荐算法
'''
# 返回p1和p2的皮尔逊相关系数
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]["movies"]:
        if item in prefs[p2]["movies"]: si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([int(prefs[p1]["movies"][it]["movie_rate"]) for it in si])
    sum2 = sum([int(prefs[p2]["movies"][it]["movie_rate"]) for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(int(prefs[p1]["movies"][it]["movie_rate"]), 2) for it in si])
    sum2Sq = sum([pow(int(prefs[p2]["movies"][it]["movie_rate"]), 2) for it in si])

    # Sum of the products
    pSum = sum([int(prefs[p1]["movies"][it]["movie_rate"]) * int(prefs[p2]["movies"][it]["movie_rate"]) for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, n=5, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person: continue
        sim = similarity(prefs, person, other)

        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]["movies"]:
            # print(item)

            # only score movies I haven't seen yet
            if item not in prefs[person]["movies"] or prefs[person]["movies"][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += int(prefs[other]["movies"][item]["movie_rate"]) * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    # print(totals.items())
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings[0:n]

def send_Recommendations(list):
    movie_list = []
    for date in list:
        sql = "SELECT * FROM s_books WHERE `name`='"+date[1]+"'"
        cursor.execute(sql)
        movie = cursor.fetchall()
        # print(movie)
        movie_list.append(movie[0])
    return movie_list

list = getRecommendations(movie_data, my_name, n=20)
print(list)
# print(send_Recommendations(list))
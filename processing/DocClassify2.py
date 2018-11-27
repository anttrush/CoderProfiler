# 停用词+词干化，构造单词表Wordlist
# 单词表筛选，构造文本矩阵corpus
# TfidfVectorizer，构造tfidf权重矩阵Wordtfidf
# 已有W2V+单词表，构造单词表Vector表示矩阵wordmatrics，每一行是一个单词的vector
# Wordtfidf · wordmatrics/M = X，M为当前行tfidf和，即用tfidf对vector加权，每一行表示一篇文章，是一个N维vector，N为vector维数
# 对X的各行做聚类

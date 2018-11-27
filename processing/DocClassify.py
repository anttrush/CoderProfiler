# coding=utf-8
'''
【数据源样例】
词语1 词语2 词语3 词语4 词语5 词语6 词语7 词语8 词语9
词语1 词语2 词语3 词语4 词语5
词语1 词语2 词语3 词语4 词语5 词语6 词语7
……
一行是一篇已切好词的文本，词语之间用空格分隔
【主要参数说明】
1.n_topics：主题个数，即需要将这些文本聚成几类
2.n_iter：迭代次数
【程序输出说明】
1.doc-topic分布：即每篇文本属于每个topic的概率，比如20个topic，那么第一篇文本的doc-topic的分布就是该文本属于这20个
topic的概率（一共20个概率数字）
2.topic-word分布：即每个topic内词的分布，包含这个词的概率/权重
3.每个topic内权重最高的5个词语
4.每篇文本最可能的topic
'''
N_TOPICS = 10   # 主题个数
import codecs
import collections
import numpy as np
import lda
from stop_words import get_stop_words
from nltk.stem.snowball import SnowballStemmer
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
# nltk.download('stopwords')

# 读取已切好词的语料库所有词语，去重
filePath = r'C:\Users\anttrush\Desktop\毕设\data'
cutWordsFile = r'\_texts.txt'  # 语料库文件，其内一行是一个已切好词的文本
corpus = []                     # ['this is a dog.', 'I'm a teacher.']
wordSet = set()                 # 单词表，字典
sw = get_stop_words('en')       # 停用词表
sw.append('-')
stopwords = nltk.corpus.stopwords.words('english')  # 停用词表
stemmer = SnowballStemmer("english")    # 词干化

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                 min_df=0.2, stop_words='english',
                                 use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

for eachLine1 in codecs.open(filePath + cutWordsFile, 'r', 'utf-8'):
    lineList1 = eachLine1.split(' ')
    for i in range(len(lineList1)):
        w = stemmer.stem(lineList1[i].strip())
        if w not in stopwords and re.search('[a-zA-Z]', w):
            wordSet.add(w)
wordList = list(wordSet)        # 单词表，字典

# 生成词频矩阵，一行一个文本，一列一个词语，数值等于该词语在当前文本中出现的频次
# 矩阵行数=文本总数，矩阵列数=语料库去重后词语总数
# 该矩阵是一个大的稀疏矩阵
wordMatrix = []
for eachLine2 in codecs.open(filePath + cutWordsFile, 'r', 'utf-8'):
    docWords = eachLine2.strip().split(' ')
    dict1 = collections.Counter(docWords)
    key1 = list(dict1.keys())
    r1 = []                     # 当前行的tf向量
    for i in range(len(wordList)):
        if wordList[i] in key1:
            r1.append(dict1[wordList[i]])
        else:
            r1.append(0)
    wordMatrix.append(r1)
    corpus.append(eachLine2)
X = np.array(wordMatrix)  # 词频矩阵
X2 = tfidf_vectorizer.fit_transform(corpus) # tfidf 矩阵

# 模型训练
model = lda.LDA(n_topics=N_TOPICS, n_iter=100, random_state=1)
model.fit(X)

# doc-topic分布
print('==================doc:topic==================')
doc_topic = model.doc_topic_
print(type(doc_topic))
print(doc_topic.shape)
print(doc_topic)  # 一行为一个doc属于每个topic的概率，每行之和为1

# topic-word分布
print('==================topic:word==================')
topic_word = model.topic_word_
print(type(topic_word))
print(topic_word.shape)
print(topic_word[:, :3])  # 一行对应一个topic，即每行是一个topic及该topic下词的概率分布，每行之和为1

# 每个topic内权重最高的5个词语
n = 5
print('==================topic top' + str(n) + ' word==================')
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(wordList)[np.argsort(topic_dist)][:-(n + 1):-1]
    print('*Topic {}\n-{}'.format(i, ' '.join(topic_words)))

# 每篇文本最可能的topic
print('==================doc best topic==================')
txtNums = len(codecs.open(filePath + cutWordsFile, 'r', 'utf-8').readlines())  # 文本总数
for i in range(10):
    topic_most_pr = doc_topic[i].argmax()
    print('doc: {} ,best topic: {}'.format(i, topic_most_pr))

'''
【程序运行结果如下】
==================doc:topic==================
<class 'numpy.ndarray'>
(6543, 10)
[[ 0.3137931   0.00344828  0.21034483 ...,  0.21034483  0.00344828
   0.00344828]
 [ 0.002       0.102       0.002      ...,  0.002       0.302       0.122     ]
 [ 0.58076923  0.00384615  0.00384615 ...,  0.35        0.00384615
   0.00384615]
 ...,
 [ 0.06        0.00285714  0.00285714 ...,  0.00285714  0.26        0.17428571]
 [ 0.05121951  0.00243902  0.19756098 ...,  0.73414634  0.00243902
   0.00243902]
 [ 0.003125    0.003125    0.003125   ...,  0.003125    0.003125    0.503125  ]]
==================topic:word==================
<class 'numpy.ndarray'>
(10, 14849)
[[  5.16569216e-07   5.16569216e-07   5.16569216e-07]
 [  4.88126565e-07   4.88126565e-07   4.88126565e-07]
 [  4.05227598e-07   4.05227598e-07   4.05227598e-07]
 [  4.64630254e-07   4.64630254e-07   4.64630254e-07]
 [  4.59569595e-07   4.59569595e-07   1.38330448e-04]
 [  5.04172278e-07   5.04172278e-07   5.04172278e-07]
 [  4.50724743e-07   4.50724743e-07   4.50724743e-07]
 [  5.32552540e-07   5.37878066e-05   5.32552540e-07]
 [  4.28183189e-07   4.28183189e-07   4.28183189e-07]
 [  4.11413842e-05   4.07340438e-07   4.07340438e-07]]
==================topic top5 word==================
*Topic 0
-5个词（涉及具体业务，具体词语已屏蔽，下同）
*Topic 1
-5个词
*Topic 2
-5个词
*Topic 3
-5个词
*Topic 4
-5个词
*Topic 5
-5个词
*Topic 6
-5个词
*Topic 7
-5个词
*Topic 8
-5个词
*Topic 9
-5个词
==================doc best topic==================
doc: 0 ,best topic: 0
doc: 1 ,best topic: 3
doc: 2 ,best topic: 0
doc: 3 ,best topic: 9
doc: 4 ,best topic: 8
doc: 5 ,best topic: 1
doc: 6 ,best topic: 9
doc: 7 ,best topic: 5
doc: 8 ,best topic: 2
doc: 9 ,best topic: 3
'''

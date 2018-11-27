import xml.sax

N_TOPICS = 10   # 主题个数
import codecs
import collections
import numpy as np
import lda
from stop_words import get_stop_words
from nltk.stem.snowball import SnowballStemmer
import nltk
import gensim
from gensim.parsing.preprocessing import STOPWORDS  # 停用词表3
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
import re
from sklearn.feature_extraction.text import TfidfVectorizer
# nltk.download('stopwords')

# 读取已切好词的语料库所有词语，去重
filePath = r'pmdRuleDocs\data'
cutWordsFile = r'\_texts.txt'  # 语料库文件，其内一行是一个已切好词的文本
corpus = []                     # ['this is a dog.', 'I'm a teacher.']
wordSet = set()                 # 单词表，字典
sw = get_stop_words('en')       # 停用词表1
stopwords = nltk.corpus.stopwords.words('english')  # 停用词表2
stemmer = SnowballStemmer("english")    # 词干化

def  tokenize_and_stem(text):
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token) and token not in STOPWORDS and token not in stopwords and token not in sw:
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

def classify():
    with open(filePath+cutWordsFile, 'r') as f:
        for line in f.readlines():
            corpus.append(line)
    print(len(corpus), corpus[0])
    processed_docs = [tokenize_and_stem(doc) for doc in corpus]





class RuleDocHandler(xml.sax.ContentHandler):
    def __init__(self, rulesetName):
        self.CurrentData = ""
        self.name = ""
        self.description = ""
        self.rulesetFile = "pmdRuleDocs/" + rulesetName +"1.xml"
        self.outputname = "pmdRuleDocs/" + rulesetName +"Name.txt"
        self.outputtext = "pmdRuleDocs/" + rulesetName +"text.txt"

    # 元素开始调用
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "rule":
            # print("*****rule*****", file=open(self.output, 'a'))
            name = attributes["name"]
            print(name, file=open(self.outputname, 'a'))

    # 元素结束调用
    def endElement(self, tag):
        if self.CurrentData == "description":
            # the first description is for whole ruleset, delete it.
            print(self.description, file=open(self.outputtext, 'a'))
        self.CurrentData = ""

    # 读取字符时调用
    def characters(self, content):
        if self.CurrentData == "description":
            self.description = content


def docParse():
    # 创建一个 XMLReader
    parser = xml.sax.make_parser()
    # 关闭命名空间
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # 重写 ContextHandler
    rulesets = {'bestpractices', 'codestyle','design', 'documentation','errorprone', 'multithreading','performance', 'security'}
    for rulesetName in rulesets:
        Handler = RuleDocHandler(rulesetName)
        parser.setContentHandler(Handler)

        parser.parse(Handler.rulesetFile)

if __name__ == '__main__':
    # docParse()
    classify()
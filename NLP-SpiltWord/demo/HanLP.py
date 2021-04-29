# -*- coding: utf-8 -*- 
'''
HanLP : https://github.com/hankcs/HanLP
'''
import hanlp
import pymongo
import jieba
import jieba.analyse

tokenizer = hanlp.load('LARGE_ALBERT_BASE')



'''
print(
    tokenizer(['萨哈夫说，伊拉克将同联合国销毁伊拉克大规模杀伤性武器特别委员会继续保持合作。',
               '上海华安工业（集团）公司董事长谭旭光和秘书张晚霞来到美国纽约现代艺术博物馆参观。',
               'HanLP支援臺灣正體、香港繁體，具有新詞辨識能力的中文斷詞系統'])
               )

print("hello world")
'''

myclient = pymongo.MongoClient("mongodb://192.168.110.130:27017/")

db = myclient["tuduweb"]
collection = db["db_movie_comment"]

item = collection.find_one()

print(item)

if item:
    content = item['content'].strip()

    print(content)

    print(tokenizer(content))
    seg_list = jieba.cut(content, cut_all=False)
    print("Default Mode: " + "/ ".join(seg_list))  # 全模式


    '''
    import jieba.analyse
    jieba.analyse.extract_tags(sentence, topK=20, withWeight=False, allowPOS=())
    #---------------------------------------------------------------------------
    sentence 为待提取的文本
    topK 为返回几个 TF/IDF 权重最大的关键词，默认值为 20
    withWeight 为是否一并返回关键词权重值，默认值为 False
    allowPOS 仅包括指定词性的词，默认值为空，即不筛选
    #---------------------------------------------------------------------------
    逆文档频率(IDF)：该此在文档库中的稀有性
    '''

    print(jieba.analyse.extract_tags(content, topK=20, withWeight=True, allowPOS=()))


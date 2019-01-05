from gensim import matutils, models, corpora
from scipy.sparse import csc_matrix
import MeCab
import os
import pathlib
import re
import pandas as pd


class Extend_MeCab():
    def __init__(self):
        self.mc = MeCab.Tagger(
            r'-d C:\Users\icech\mecab-ipadic-neologd\build\mecab-ipadic-2.7.0-20070801-neologd-20180625')

    def make_lines(self, txt, Flg_matubi=False):
        txt=re.sub('\（.+\）','',txt)
        txt=re.sub('.+　','',txt)
        txt=re.sub('\n','',txt)
        txt=re.sub('\\u3000','',txt)
        txt=txt.split('。')
        for sentence in txt:
            if Flg_matubi == True:
                sentence = re.sub('.+、', '', sentence)
            morphemes = []

            wakatis = self.mc.parse(sentence)
            wakatis = wakatis.split('\n')
            for wakati in wakatis:
                if wakati == 'EOS'or'':
                    yield morphemes
                    break

                cols = wakati.split('\t')
                res_cols = cols[1].split(',')
                morpheme = {
                    'surface': cols[0],
                    'base': res_cols[6],
                    'pos': res_cols[0]}
                morphemes.append(morpheme)

    def count_morpheme(self, txt, word_class='動詞'):
        txt_word_list = []
        for morphemes in self.make_lines(txt, Flg_matubi=False):
            for morpheme in morphemes:
                if len(morpheme['base']) == 1:
                    continue

                if morpheme['pos'] == word_class:
                    txt_word_list.append(morpheme['base'])
        # 二重リストで返す
        return([txt_word_list])

    def count_matubi(self, txt, max_matubi_len=4):
        matubi_list = []
        for morphemes in self.make_lines(txt, Flg_matubi=True):
            sentence = [d.get('surface') for d in morphemes]

            word = ""
            max_matubi_len = min([len(sentence), max_matubi_len])

            for i in reversed(range(1, max_matubi_len+1)):
                word += sentence[-i]

            matubi_list.append(word)

        return([matubi_list])


class Preprocessing_txt():
    def __init__(self):
        self.corpus_dic = corpora.Dictionary()
        self.corpus_list = []

    def subscribe_dic(self):
        print(f'全単語数={len(self.corpus_dic)}')
        print(f'全語数={self.corpus_dic.num_pos}')
        print(f'全文書数={self.corpus_dic.num_docs}')
        print(f'単語id={self.corpus_dic.token2id}')

    def update_copus(self, devide_word_list):
        self.corpus_dic.add_documents(devide_word_list)
        self.corpus_list.extend([self.corpus_dic.doc2bow(devide_word_list[0],allow_update=True)])

    def dic2df(self):
        keys = [key for key in self.corpus_dic.token2id]

        df = pd.DataFrame(index=range(len(self.corpus_list)), columns=keys)
        for j, corpus in enumerate(self.corpus_list):
            for cor in corpus:
                df.iat[j, cor[0]] = cor[1]
        df.fillna(0,inplace=True)

        return(df)
    
    def save_data(self,filename):
        self.corpus_dic.save(filename)
        # df=self.dic2df()


































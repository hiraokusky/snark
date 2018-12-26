"""
Copyright 2018 hiraokusky

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sqlite3
import time
import random
import pandas as pd

from wordnetdb import WordNetDb, SynSet

# フレーズのパターンを定義したWordNet構造に沿ったDB
# フレーズのデータはposで区別
# posで前置句か後置句か決める, pはまだ続くことを示し、qは終わることを示す
# 名詞+中間->np, 助詞など
# 開始->p, 接続詞など
# 開始+名詞->pn, 形容詞など
# 接頭+名詞->on, お-など
# 名詞+接尾->no, -ちゃんなど
# 名詞+終了->nq, 助動詞など
# 動詞+終了->vq, 活用など
# synset:-を -> word:lemma:を

# 深層格
# 動作主格 case_agentive
# 経験者格 case_experiencer
# 道具格 case_instrumental
# 対象格 case_objective
# 源泉格 case_source
# 目標格 case_goal
# 場所格 case_locative
# 時間格 case_time
# 経路格 case_path

# senseの定義を変える
# 使うシーンを示す。これによって、そのフレーズが使われるシーンを特定する
# src:使うシーンの定義/例文
# 例文はフレームを表す。どこ誰いつの文かを示す。つまり、@文の場所>文という構造。

# phrasenetでは読み込んだ文をsynsetとして記憶する
# synsetdefのnameをlemmaとする
# これでsenseの定義を代替する

# phrasenetで記憶する文
# synsetdef:glossに保存する

# 文は全体部分構造で保存する
# 

class PhraseNetDb:
    wn = WordNetDb()

    # 外部辞書
    startdict = pd.DataFrame()
    verbdict = pd.DataFrame()

    # パターン辞書
    def load(self):
        self.startdict = pd.read_csv('dict/phrases.csv', header=None)
        self.startdict = self.startdict.fillna('')

        self.verbdict = pd.read_csv('dict/verbs.csv', header=None)
        self.verbdict = self.verbdict.fillna('')
        
    def train(self):
        # AがBした
        self.add_post('が', 'case_agentive', 'np')
        # AはBである
        self.add_post('は', 'case_agentive', 'np')

    def add_post(self, name, synset, pos, lang='jpn'):
        self.wn.add_word(name, synset, 'np')

    def add_start(self, name, synset, pos, lang='jpn'):
        self.wn.add_word(name, synset, 'p')

    def add_pre(self, name, synset, pos, lang='jpn'):
        self.wn.add_word(name, synset, 'pn')

    def add_end(self, name, synset, pos, lang='jpn'):
        self.wn.add_word(name, synset, 'nq')

    def add_verb(self, name, synset, pos, lang='jpn'):
        self.wn.add_word(name, synset, 'vq')

    def add_frame(self, prev, frame):
        """
        フレームを記憶する
        Notes
        -----
        前のフレームを指定して、フレーム文を記憶します。
        """
        self.wn.add_synlink(prev, 'f', frame, 'f', 'frame')

    def add_phrase(self, frame, prev, phrase):
        """
        文を記憶する
        Notes
        -----
        フレームと前の文を指定して、文を記憶します。
        """
        synset = self.wn.add_synsetdef('', phrase, 's')
        self.wn.add_synlink(frame, 'f', synset, 's', 'phrase')
        if len(prev) > 0:
            self.wn.add_synlink(prev, 's', synset, 's', 'next')
        return synset

    def get_frame_info(self, frame):
        info = self.wn.get_synlink_info_by_name(frame)
        return info

    # 文字列からフレーズを取得
    def get_phrase(self, name, pos):
        words = self.wn.get_words(name, pos)
        return words

def phrasenetdb_test_print(pn, frame):
    print(frame)
    cur = pn.get_frame_info(frame)
    for f in cur:
        print(f)

def phrasenetdb_test():
    pn = PhraseNetDb()
    title = '概念化と言語化'
    pn.add_frame('root', title)
    frame = '何を語り何を語らないか ､ 何を聞き何を聞かないか'
    pn.add_frame(title, frame)
    phrase = ''
    phrase = pn.add_phrase(frame, phrase, '言説における人間の思考過程は、§ 3 で述べたように、概念のネットワークというよりむしろ言語化されたことばの意味に基づいている。')
    phrase = pn.add_phrase(frame, phrase, 'こうした視点に立ってはじめて本節の表題のような問いを発することができる。')

    phrasenetdb_test_print(pn, frame)

phrasenetdb_test()

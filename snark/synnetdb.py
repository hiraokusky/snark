"""
Copyright 2019 hiraokusky

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
import pandas as pd
import numpy as np
import re
import json
import sys,os

# pip install git+https://github.com/hiraokusky/snark
from snark import wordnetdb, kanadb

class SynNetDb:
    """
    wordnetを簡単に処理するための一時記憶
    RDF DBも併せて処理する

    word in synset . 同義語, 個物化
    synset isa synset . 抽象化, 属性
    synset hasa synset . 部分/属性/材質/所有(目的語を抱えている状態の主語)
    synset then synset . 状態遷移(主語から主語へ移る), 条件つきの場合は条件の付いたsynsetができる
    """

    startdict = None

    v = False

    def __init__(self, opts=''):
        self.v = 'v' in opts

    def load_file(self, path):
        self.startdict = pd.read_csv(path)
        self.startdict = self.startdict.fillna('')

    def save_file(self, path):
        self.startdict.to_csv(path, index=False)

    def load_same_words_from_db(self, path, key):
        wn = wordnetdb.WordNetDb(path)
        cur = wn.get_same_words_by_lemma(key)
        for c in cur:
            self.add_link(c[3], 'in', c[1])

    def select(self, key):
        d = self.startdict
        res = d[d['synset1'] == key]
        return res

    def select_link(self, key, link='isa'):
        d = self.startdict
        res = d[(d['synset1'] == key) & (d['link'] == link)]
        l = []
        for r in res.values:
            l.append(r[2])
        return l

    def select_link_ref(self, key, link='isa'):
        d = self.startdict
        res = d[(d['synset2'] == key) & (d['link'] == link)]
        l = []
        for r in res.values:
            l.append(r[0])
        return l

    def select_isa(self, key):
        """
        isaリンクとinリンクを持つ全synsetを取得する
        Returns
        -------
        [synset, ...]
        """
        d = self.startdict
        res = d[(d['synset1'] == key) & ((d['link'] == 'in') | (d['link'] == 'isa'))]
        l = []
        for r in res.values:
            l.append(r[2])
        return l

    def select_same(self, key):
        """
        keyと同じinを持つ全synsetを取得する
        Returns
        -------
        [(synset, [word, ...]), ...]
        """
        isa = self.select_link(key, 'in')
        res = []
        for i in isa:
            ref = self.select_link_ref(i, 'in')
            res.append((i, ref))
        return res

    def add_link(self, synset1, link, synset2):
        """
        リンクを追加する
        同じデータがあれば追加しない
        """
        d = self.startdict
        res = d[(d['synset1'] == synset1) & (d['link'] == link) & (d['synset2'] == synset2) ]
        if len(res) == 0:
            tmp_se = pd.Series([synset1, link, synset2], index=['synset1', 'link', 'synset2'])
            self.startdict = self.startdict.append(tmp_se, ignore_index=True)

# wordnetdbからデータをロードする
# rn = SynNetDb(opts='v')
# rn.load_file('dict/rn.csv')
# print(rn.select_isa('犬'))
# rn.add_link('犬', 'isa', '動物')
# print(rn.select_same('犬'))

# rn.load_same_words_from_db('db/wnjpn.db', '犬')
# rn.save_file('dict/rn.csv')
# print(rn.select_same('犬'))
# rn.add_link('ネコ', 'isa', '動物')
# print(rn.select_link_ref('動物', 'isa'))

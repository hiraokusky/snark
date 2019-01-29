"""
Copyright 2018-2019 hiraokusky

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
    """

    startdict = None

    def load_file(self, path):
        self.startdict = pd.read_csv(path)
        self.startdict = self.startdict.fillna('')

    def save_file(self, path):
        self.startdict.to_csv(path)

    def load_isa_words_from_db(self, path, key):
        wn = wordnetdb.WordNetDb(path)

        cur = wn.get_same_words_by_lemma(key)
        for c in cur:
            self.add_link(c[3], 'isa', c[1])

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

    def select_eq(self, key):
        d = self.startdict
        link = 'eq'
        res = d[((d['synset1'] == key) | (d['synset2'] == key)) & (d['link'] == link)]
        l = []
        for r in res.values:
            l.append(r[0])
            l.append(r[2])
        return list(set(l))

    def add_link(self, synset1, link, synset2):
        tmp_se = pd.Series([synset1, link, synset2], index=['synset1', 'link', 'synset2'])
        self.startdict = self.startdict.append(tmp_se, ignore_index=True)

# wordnetdbからデータをロードする
rn = SynNetDb()
rn.load_file('dict/rn.csv')
print(rn.select('d'))
print(rn.select_link('犬', 'isa'))

rn.load_isa_words_from_db('db/wnjpn.db', '犬')
print(rn.select_eq('犬'))
# rn.add_link('ネコ', 'isa', '動物')
# print(rn.select_link_ref('動物', 'isa'))

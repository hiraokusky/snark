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
import sys
import os

# pip install git+https://github.com/hiraokusky/snark
from snark import wordnetdb, kanadb
from snark import fu

class PhraseNetDb:

    # かな変換辞書
    kn = kanadb.KanaDb()

    # 外部辞書
    startdict = pd.DataFrame()

    def __init__(self, path):
        self.wn = wordnetdb.WordNetDb(path)

    def load_file(self, path):
        """
        フレーズ辞書をファイルからロードする
        """
        self.startdict = pd.read_csv(path, header=None)
        self.startdict = self.startdict.fillna('')

    def load_db(self, path):
        """
        フレーズ辞書をWordNetDbからロードする
        """
        wn = wordnetdb.WordNetDb(path)

        d = wn.get_synset_def_all(
            ['r', 'a', 'n', 'p', 't', 'v', 'w', 'f', 'e'])
        for c in d:
            dict_pos = c[0]
            dict_src = c[3]
            dict_pron = ''
            cc = c[2].split()
            if len(cc) > 1:
                dict_pron = cc[0]
                dict_word = cc[1]
            elif len(cc) == 1:
                dict_word = cc[0]
            else:
                continue
            tmp_se = pd.Series([dict_pos, dict_word, dict_src, dict_pron])
            self.startdict = self.startdict.append(tmp_se, ignore_index=True)

    def save_db(self, path):
        """
        フレーズ辞書をWordNetDnに保存する
        """
        wn = wordnetdb.WordNetDb(path)

        data = []
        for p in self.startdict.values:
            dict_pos = p[0]
            if len(dict_pos) > 0 and dict_pos != 'synset':
                dict_word = p[1]
                dict_synset = p[3]
                dict_pron = p[2]
                if len(dict_pron) > 0:
                    dict_word = dict_pron + ' ' + dict_word
                data.append((dict_pos, 'jpn', dict_word, 'pn'))
        wn.insert_synset_def_all(data)

    def _match_phrase_type(self, t, word):
        for p in self.startdict.values:
            dict_pos = p[0]
            dict_word = p[1]
            if len(dict_pos) > 0 and dict_pos[0] == t and len(dict_word) > 0 and word.startswith(dict_word):
                return True
        return False

    def parse_conditions(self, s):
        """
        /a#b形式を配列に分解する
        """
        d = s.split('#')
        if len(d) > 1:
            # /がある
            e = d[0].split('/')
            if len(e) > 1:
                return [e[1:], d[1:]]
            return [[], d[1:]]
        e = s.split('/')
        if len(e) > 1:
            return [e[1:], d[1:]]
        return []

    def get_phrases(self, s, pre='', pret=''):
        """
        一致するフレーズを取得する

        Parameters
        ----------
        s: 検査文字列(必須)
        pre: 直前の文字(なければ'')
        pret: 直前の品詞(なければ'')

        Returns
        -------
        [[ フレーズ /直前の品詞#直前の発音 残りの文] ... ]
            先頭一致するフレーズの最長順のリスト
            これを使い次をget_phrasesして、空だったものを候補から脱落させる
            残ったもので候補リストを再構成する
        """
        pre = self.kn.to_romaji(pre)
        l = 0
        matches = []
        for p in self.startdict.values:
            dict_pos = p[0]
            dict_word = p[1]
            dict_synset = p[3]
            dict_pron = p[2]
            q = [dict_pos, dict_word, dict_synset, dict_pron]
            # print(dict_pos, dict_word, dict_synset, dict_pron)

            if len(dict_pos) > 0:
                if len(pret) > 0:
                    if pret[0] == 'v':
                        # 動詞の直後は動詞接続w
                        if dict_pos[0] == 'w':
                            a = 0
                        # もしくは記号e
                        elif dict_pos[0] == 'e':
                            a = 0
                        # もしくは名詞n
                        elif dict_pos[0] == 'n':
                            a = 0
                        else:
                            continue
                    # 動詞接続wの場合、直前は動詞vでないといけない
                    if dict_pos[0] == 'w' and pret[0] != 'v':
                        continue
                    # 名詞終わり文tの場合、直前は名詞nでないといけない
                    if dict_pos[0] == 't' and pret[0] != 'n':
                        continue
                    # 名詞後付加pの場合、直前は名詞nでないといけない
                    if dict_pos[0] == 'p' and pret[0] != 'n':
                        continue

            if len(dict_pos) > 0:
                if dict_pos[0] == 'v':
                    # 動詞の活用と一致するものを選択
                    w = self.get_verb_ends(s, dict_word)
                    if w != None:
                        dict_word = w
                        q[1] = w
                        # 次の文字が平仮名でなければvではない
                        if len(s) > len(w) and not self.kn.is_hiragana(s[len(w):][0]):
                            continue
                    else:
                        continue

                if dict_pos[0] == 'a':
                    # 形容詞の活用と一致するものを選択
                    w = self.get_adj_ends(s, dict_word)
                    if w != None:
                        dict_word = w
                        q[1] = w
                    else:
                        continue

            if len(dict_word) > 0 and s.startswith(dict_word):
                match = False

                # 接続パターンがない場合
                if len(pre) == 0 or len(dict_pos) <= 1:
                    match = True
                # 接続パターンがある場合はパターンに一致する場合のみ一致
                elif pre.endswith(dict_pron):
                    match = True

                # # 文終わりf品詞の場合、直後はe記号でないといけない
                if dict_pos[0] == 'f' and not self._match_phrase_type('e', s[len(dict_word):]):
                    match = False

                if match:
                    # 最長一致する
                    if len(dict_word) > l:
                        l = len(dict_word)
                        matches.insert(0, q)
                    else:
                        matches.append(q)

        return matches

    def get_verb_ends(self, s, word):
        """
        get_verb_ends(元の文字列, 動詞原型) -> 元の文字列の動詞活用形部分
        """
        c = word[len(word) - 1]
        w = word[:len(word) - 1]
        if c == 'う':  # 会う
            d = ['わ', 'い', 'う', 'え', 'お', 'った', 'って']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'く':  # 書く
            d = ['か', 'き', 'く', 'け', 'こ', 'いた', 'いて']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'す':  # 指す
            d = ['さ', 'し', 'す', 'せ', 'そ', 'した', 'して']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'つ':  # 勝つ
            d = ['た', 'ち', 'つ', 'て', 'と', 'った', 'って']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'ぬ':  # 死ぬ
            d = ['な', 'に', 'ぬ', 'ね', 'の', 'んだ', 'んで']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'ぶ':  # 尊ぶ
            d = ['ば', 'び', 'ぶ', 'べ', 'ぼ', 'んだ', 'んで']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'む':  # 噛む
            d = ['ま', 'み', 'む', 'め', 'も', 'んだ', 'んで']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        if c == 'る':  # 得る→得て, 探る→探って
            d = ['ら', 'り', 'る', 'れ', 'ろ', 'よ', 'った', 'って', 'た', 'て', '']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        return None

    def get_adj_ends(self, s, word):
        """
        get_adj_ends(元の文字列, 形容詞原型) -> 元の文字列の形容詞活用形部分
        """
        c = word[len(word) - 1]
        w = word[:len(word) - 1]
        if c == 'い':  # 楽しい
            d = ['い', 'な', 'かった', 'く', 'そう', 'くて', 'くない', 'けれ']
            for e in d:
                if s.startswith(w + e):
                    return w + e
        return None

    def add_context(self, tokens, context):
        """
        解析したトークンからコンテキストをつくる
        トークンからイメージスキーマ言語をつくる
        """
        # 1. 記述フレーム特定
        # その文の記述の意図を把握

        # 項目のsynsetを利用して項目の意味を知る
        # →すごい、結構いける

        # 日時
        if ':date' in tokens[0][0]:
            if self.match_time_schema(context, tokens):
                return

    def match_time_schema(self, context, tokens):
        # 日付と同じ意味を持つ単語を取得して,つなぎにする
        tword = self.get_synonyms('日付')

        schema = [[ tword, '', '' ], [':', '', ''], ['', 'z', ''], ['年', '', ''], ['', 'z', ''], ['月', '', ''],['', 'z', ''], ['日', '', '']]
        if self.match_schema(schema, tokens) != None:
            context.append(['date', schema[2][0], schema[4][0], schema[6][0]])
            return True

        schema = [[ tword, '', '' ], [':', '', ''], ['', 'z', ''], ['月', '', ''], ['', 'z', ''], ['日', '', '']]
        if self.match_schema(schema, tokens) != None:
            context.append(['date', schema[2][0], schema[4][0]])
            return True

        return False
        
    def get_synonyms(self, word):
        """
        類義語リストを作る
        """
        return fu.array2_to_str(self.wn.get_same_words_by_lemma(word), 3)

    def match_schema(self, schema, tokens):
        """
        トークン列からスキーマを見つける
        """
        i = 0
        for t in tokens:
            word = t[0]
            pos = t[1]
            typ = t[2]
            tword = schema[i][0]
            tpos = schema[i][1]
            ttyp = schema[i][2]
            if len(tword) > 0 and not fu.match(word, tword):
                continue
            if len(tpos) > 0:
                if not fu.match(pos, tpos):
                    continue
                else:
                    schema[i][0] = word
            if len(ttyp) > 0:
                if not fu.match(typ, ttyp):
                    continue
                else:
                    schema[i][0] = word
            i += 1
            if len(schema) == i:
                return tokens[i:]
        return None

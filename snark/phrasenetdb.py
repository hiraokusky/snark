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


class PhraseNetDb:
    """
    # root synset

    r=
    主に文の始めに現れるフレーズ。
    接続詞の他、感嘆詞など。

    a=形容詞
    対象の名詞を見た心象を相手に伝えるためのフレーズ。意味は等価。

    p:
    名詞に接続するフレーズ。名詞に役割を与える。

    t:
    名詞で終わる文、つまり、等価を示す文の終わりに現れるフレーズ。
    であろう、など。

    v:
    動詞

    w:
    動詞で終わる文、つまり、変化を示す文の終わりに現れるフレーズ。

    f:
    会話文の終わりに現れる、人の特徴を示すフレーズ。
    ～だぜ、など。

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

    フレーズネット
    synset: 品詞
    synset_def: フレーズ

    フレーズの接続ルールを表現する
    #i ねえ /e: 直前の音のルール(to_romajiした文字列)
    /v#u れる: 品詞の並びのルール(synset), /を複数書くとOR条件, #を複数書くとOR条件
    /n は /n である: フレーズの並びのルール

    BNFを表現する
    synset :== synset list
    """

    # かな変換辞書
    kn = kanadb.KanaDb()

    # 外部辞書
    startdict = pd.DataFrame()

    def load_file(self, path):
        """
        フレーズ辞書をロードする
        """
        self.startdict = pd.read_csv(path, header=None)
        self.startdict = self.startdict.fillna('')

    def load_db(self, path):
        """
        フレーズ辞書をWordNetDbからメモリにロードする
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
            # print(dict_pos, dict_word, dict_src, dict_pron)

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
                data.append((dict_pos, 'jpn', dict_word, 'pnjpn.db'))
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
        先頭一致するフレーズの最長順のリスト
        [[ フレーズ /直前の品詞#直前の発音 残りの文] ... ]
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


# p = PhraseNetDb()
# print(p.parse_conditions('/a'))
# print(p.parse_conditions('/a/d'))
# print(p.parse_conditions('/a#b'))
# print(p.parse_conditions('#b'))
# print(p.parse_conditions('#b#c'))
# print(p.parse_conditions('/a/d#b'))
# print(p.parse_conditions('/a/d#b#c'))

# p.load_file('dict/phrases.csv')
# p.save_db('db/wnjpn.db')
# p.load_db('db/wnjpn.db')

# print(p.get_verb_ends('知ってるな', '知る'))
# print(p.get_adj_ends('美しくってね', '美しい'))
# print(p.get_phrases('知識'))
# print(p.get_phrases('知ってね'))

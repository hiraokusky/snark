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
import networkx as nx
import matplotlib

class Word:
    wordid = 0  # ワードID(8桁は予約)
    lang = 'jpn'  # 言語
    lemma = ''  # ワード
    pron = None  # 読み
    pos = 'n'  # 品詞 n=名詞, v=動詞, a=形容詞, r=副詞

    def __init__(self, wordid, lang, lemma, pron, pos):
        self.wordid = wordid
        self.lang = lang
        self.lemma = lemma
        self.pron = pron
        self.pos = pos

class Sense:
    synset = ''  # 参照概念ID
    wordid = 0  # 参照ワードID
    lang = 'jpn'  # 言語
    rank = None  # 
    lexid = None  # 
    freq = None
    src = ''  # 

    def __init__(self, synset, src=''):
        self.synset = synset
        self.src = src

class SynSet:
    synset = ''  # 概念ID(8桁は予約)
    pos = 'n'  # 品詞
    name = ''  # 概念
    src = ''  # 

    def __init__(self, synset, pos='', name='', src=''):
        self.synset = synset
        self.pos = pos
        self.name = name
        self.src = src

class SynSetDef:
    synset = ''  # 参照概念ID
    name = ''  # 概念名
    lang = 'jpn'  # 言語
    gloss = ''  # 例文
    sid = '0'  # 

    def __init__(self, synset, name, gloss):
        self.synset = synset
        self.name = name
        self.gloss = gloss

class SynLink:
    synset1 = ''  # 概念ID
    synset2 = ''  # 概念ID
    link = 'hypo'  # 関係
    sid = '0'

    def __init__(self, synset1, synset2, link):
        self.synset1 = synset1
        self.synset2 = synset2
        self.link = link

class WordNetDb:
    def __init__(self):
        self.conn = sqlite3.connect('db/wnjpn.db')

    def __enter__(self):
        return self

    def __del__(self):
        self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _create_word_id(self):
        return int(time.time() * 100)

    def _create_synset_id(self, pos):
        return str(self._create_word_id()) + '-' + pos

    def _get_word_by_name(self, name, lang='jpn'):
        cur = self.conn.execute(
            'select * from word where (lemma=? and lang=?)', (name, lang))
        return cur

    def _get_word_by_name_nolang(self, name, pos):
        if len(pos) > 0:
            cur = self.conn.execute("select * from word where (lemma='%s' and pos='%s')" % (name, pos))
        else:
            cur = self.conn.execute("select * from word where lemma='%s'" % name)
        return cur

    def _get_synset_by_name(self, name):
        cur = self.conn.execute("select * from synset where name='%s'" % name)
        return cur

    def _get_synlink(self, synset1, synset2, link):
        cur = self.conn.execute(
            "select * from synlink where (synset1='%s' and synset2='%s' and link='%s')" % (synset1, synset2, link))
        return cur

    def _get_synsetdef_by_gloss(self, synset_id, gloss, lang='jpn'):
        if len(synset_id) > 0:
            cur = self.conn.execute(
                'select * from synset_def where (synset=? and def=? and lang=?)', (synset_id, gloss, lang))
        else:
            cur = self.conn.execute(
                'select * from synset_def where (def=? and lang=?)', (gloss, lang))
        return cur

    # ワードを記憶する
    def add_word(self, name, synset=None, pos='n', lang='jpn'):
        src = 'snark'
        wid = 0
        sid = 0
        commit = False

        # まずワードにあるか調べる
        cur = self._get_word_by_name(name, lang)
        c = cur.fetchone()
        if c == None:
            # なければワードに追加
            while True:
                wid = self._create_word_id()
                if self.get_word(wid) == None:
                    break
            w = (wid, lang, name, None, pos)
            self.conn.execute('INSERT INTO word VALUES(?,?,?,?,?)', w)
            commit = True
        else:
            wid = c[0]

        # 概念があるか調べる
        if synset != None:
            name = synset
        (sid, commit) = self._add_synset(name, pos, commit)

        if commit:
            # ワードと概念のリンクを追加
            l = (sid, wid, lang, None, None, None, src)
            self.conn.execute('INSERT INTO sense VALUES(?,?,?,?,?,?,?)', l)
            self.conn.commit()

    # ワードを忘れる
    def delete_word(self, name, lang='jpn'):
        wids = []
        sids = []
        commit = False

        cur = self._get_word_by_name(name, lang)
        for c in cur:
            # ワードIDに一致するwordとsenseを削除
            wids.append(c[0])
            self.conn.execute('DELETE FROM word WHERE wordid=?', (c[0],))
            self.conn.execute('DELETE FROM sense WHERE wordid=?', (c[0],))
            commit = True

        cur = self._get_synset_by_name(name)
        for c in cur:
            # 概念IDに一致するsynsetとsenseとsynset_defとsynlinkを削除
            sids.append(c[0])
            self.conn.execute('DELETE FROM synset WHERE synset=?', (c[0],))
            self.conn.execute('DELETE FROM sense WHERE synset=?', (c[0],))
            self.conn.execute(
                'DELETE FROM synset_def WHERE (synset=? and lang=?)', (c[0], lang))
            self.conn.execute(
                'DELETE FROM synlink WHERE (synset1=? or synset2=?)', (c[0], c[0]))
            commit = True

        if commit:
            self.conn.commit()

    def add_synlink(self, synset1, pos1, synset2, pos2, link):
        """
        概念リンクを追加する, 概念がなければ追加する
        """
        src = 'snark'
        commit = False

        cur1 = self._get_synset_by_name(synset1)
        c1 = cur1.fetchone()
        if c1 == None:
            (sid1, commit) = self._add_synset(synset1, pos1, commit)
        else:
            sid1 = c1[0]
            pos1 = c1[1]

        cur2 = self._get_synset_by_name(synset2)
        c2 = cur2.fetchone()
        if c2 == None:
            (sid2, commit) = self._add_synset(synset2, pos2, commit)
        else:
            sid2 = c2[0]
            pos2 = c2[1]

        cur3 = self._get_synlink(sid1, sid2, link)
        c3 = cur3.fetchone()
        if c3 == None:
            s = [sid1, sid2, link, src]
            self.conn.execute('INSERT INTO synlink VALUES(?,?,?,?)', s)
            commit = True

        if commit:
            self.conn.commit()

    def _add_synset(self, name, pos, commit):
        src = 'snark'
        c = None

        if len(name) > 0:
            # 概念があるか調べる
            cur = self._get_synset_by_name(name)
            c = cur.fetchone()
        if c == None:
            # なければ概念に追加
            while True:
                sid = self._create_synset_id(pos)
                if self.get_synset(sid) == None:
                    break
            if len(name) == 0:
                name = sid
            s = (sid, pos, name, src)
            self.conn.execute('INSERT INTO synset VALUES(?,?,?,?)', s)
            commit = True
        else:
            sid = c[0]

        return (sid, commit)

    def add_synsetdef(self, synset, gloss, pos='n', lang='jpn'):
        """
        文を記憶する

        Prameters
        ---------
        synset : str
            概念名
        gloss : str
            文
        pos : str
            品詞ID
        lang : str
            言語ID

        Returns
        -------
        概念名
        """
        src = 'snark'
        sid = 0
        commit = False

        (sid, commit) = self._add_synset(synset, pos, commit)
        if len(synset) == 0:
            synset = sid

        cur = self._get_synsetdef_by_gloss(sid, gloss, lang)
        c = cur.fetchone()
        if c == None:
            w = (sid, lang, gloss, src)
            self.conn.execute('INSERT INTO synset_def VALUES(?,?,?,?)', w)
            commit = True

        if commit:
            self.conn.commit()

        return synset

    # 文を忘れる
    def delete_synsetdef(self, gloss, lang='jpn'):
        commit = False

        cur = self._get_synsetdef_by_gloss('', gloss, lang)
        for c in cur:
            self.conn.execute('DELETE FROM synset_def WHERE def=?', (c[2],))
            commit = True

        if commit:
            self.conn.commit()

    # 名前からワードを取得
    def get_words(self, name, pos=''):
        cur = self._get_word_by_name_nolang(name, pos)
        words = []
        for row in cur:
            words.append(Word(row[0], row[1], row[2], row[3], row[4]))
        return words

    # ワードIDからワードを取得
    def get_word(self, wordid):
        cur = self.conn.execute(
            "select * from word where wordid='%s'" % wordid)
        w = cur.fetchone()
        if w:
            return Word(w[0], w[1], w[2], w[3], w[4])
        else:
            return None

    # 概念に紐づくワードを取得
    def get_words_by_sense(self, synset):
        cur = self.conn.execute(
            "select * from sense where synset='%s'" % synset.synset)
        words = []
        for row in cur:
            w = self.get_word(row[1])
            words.append(w)
        return words

    # ワードから概念を取得
    def get_synsets(self, word):
        cur = self.conn.execute(
            "select * from sense where wordid='%s'" % word.wordid)
        synsets = []
        for row in cur:
            sense = Sense(row[0])
            row2 = self.get_synset(sense.synset)
            if row2 != None:
                synsets.append(row2)
        return synsets

    # 概念IDから概念を取得
    def get_synset(self, synsetid):
        cur = self.conn.execute(
            "select * from synset where synset='%s'" % synsetid)
        w = cur.fetchone()
        if w:
            return SynSet(w[0], w[1], w[2], w[3])
        else:
            return None

    # 概念から説明を取得
    def get_synsetdefs(self, synset, lang='jpn'):
        cur = self.conn.execute(
            "select * from synset_def where (synset='%s' and lang='%s')" % (synset.synset, lang))
        synsets = []
        for row in cur:
            synsets.append(SynSetDef(row[0], synset.name, row[2]))
        return synsets

    # 関係先を取得
    def get_synlink2(self, synset, link=''):
        if len(link) > 0:
            cur = self.conn.execute(
                "select * from synlink where (synset1='%s' and link='%s')" % (synset.synset, link))
        else:
            cur = self.conn.execute(
                "select * from synlink where synset1='%s'" % synset.synset)
        hierarchy_dict = []
        for w in cur:
            hierarchy_dict.append(SynLink(w[0], w[1], w[2]))
        return hierarchy_dict

    def get_word_info_by_lemma(self, lemma):
        """
        単語と同じ概念を持つ同義語をすべて取得する
        Parameters
        ----------
        lemma : str
            単語
        Returns
        -------
        [[synset-id type id name pos-id] ...]
            概念
            概念のワード
        """
        cur = self.get_words(lemma)
        result = []
        for w in cur:
            result.extend(self.get_word_info(w))
        return result

    def get_word_info(self, w):
        """
        ワードと同じ概念を持つ同義語をすべて取得する
        Parameters
        ----------
        w : Word
            ワードオブジェクト
        Returns
        -------
        [[synset-id type id name pos-id] ...]
            概念
            概念のワード
        """
        info = []
        if not w:
            return info
        cur0 = self.get_synsets(w)
        for s in cur0:
            info.extend(self.get_synset_info(s))
        return info

    def get_wordlink_info_by_lemma(self, lemma):
        """
        単語と同じ概念に関係する概念を持つ同義語をすべて取得する
        Parameters
        ----------
        lemma : str
            単語
        Returns
        -------
        [[synset-id type id name pos-id] ...]
            概念との関係
            関係する概念
            関係する概念のワード
        """
        cur = self.get_words(lemma)
        result = []
        for w in cur:
            result.extend(self.get_wordlink_info(w))
        return result

    # 関連する概念の単語をすべて取得する
    def get_wordlink_info(self, w):
        """
        ワードと同じ概念に関係する概念を持つ同義語をすべて取得する
        Parameters
        ----------
        w : Word
            ワードオブジェクト
        Returns
        -------
        [[synset-id type id name pos-id] ...]
            概念との関係
            関係する概念
            関係する概念のワード
        """
        info = []
        if not w:
            return info
        cur0 = self.get_synsets(w)
        for s in cur0:
            info.extend(self.get_synlink_info(s))
        return info

    def get_synlink_info_by_name(self, synset_name):
        """
        概念名の概念に関係する概念を持つ同義語をすべて取得する
        Parameters
        ----------
        synset_name : str
            概念名
        Returns
        -------
        [[synset-id type id name pos-id] ...]
            概念との関係
            関係する概念
            関係する概念のワード
        """
        cur0 = self._get_synset_by_name(synset_name)
        info = []
        for s in cur0:
            synset = SynSet(s[0], s[1], s[2], s[3])
            info.extend(self.get_synlink_info(synset))
        return info

    # 概念に紐づく単語をすべて取得する
    def get_synset_info(self, s, parent=''):
        info = []
        if not s:
            return info
        cur1 = self.get_synsetdefs(s)
        gloss = ''
        for row1 in cur1:
            if len(gloss) > 0:
                gloss += ","
            gloss += row1.gloss
        info.append([parent, "synset", s.synset, s.name, s.pos, gloss])
        words = self.get_words_by_sense(s)
        for w in words:
            info.append([s.synset, "word", w.wordid, w.lemma, w.pos])
        return info

    # リンクされている概念に紐づく単語をすべて取得する
    def get_synlink_info(self, s):
        info = []
        if not s:
            return info
        # 関係先しか取得しない
        # 関係元しかない関係は、この概念からのリンクがまだ学習されていないことを示す
        synlinks = self.get_synlink2(s)
        cur2 = []
        for row in synlinks:
            row1 = self.get_synset(row.synset2)
            if row1 != None:
                cur2.append(
                    [s.synset, row.link, row1.synset, row1.name, row1.pos])
        for row2 in cur2:
            info.append(row2)
            synset = self.get_synset(row2[2])
            info.extend(self.get_synset_info(synset, s.synset))
        return info

    def get_imagenet_uris(self, lemma):
        """
        ワードを含む概念のImageNetのURIを取得する
        Parameters
        ----------
        synset_name : str
            概念名
        Returns
        -------
        [ImageNet-URI ...]
            ImageNetのURI
        """
        info = []
        if not lemma:
            return info
        base = 'http://image-net.org/synset?wnid='
        cur = self.get_words(lemma)
        result = []
        for c in cur:
            cur0 = self.get_synsets(c)
            for s in cur0:
                s.synset
                result.append(base + s.pos + s.synset[:-2])
        return result

def wordnetdb_test_print(wn, word):
    print(word)
    cur = wn.get_word_info_by_lemma(word)
    for w in cur:
        print(w)
    print('SynLink')
    cur = wn.get_wordlink_info_by_lemma(word)
    for w in cur:
        print(w)

def wordnetdb_test():
    wn = WordNetDb()

    wn.add_word('にゃんこ', 'true_cat')
    wn.add_synsetdef('true_cat', 'にゃんこ大戦争')
    wordnetdb_test_print(wn, 'にゃんこ')

    wn.delete_word('にゃんこ')
    wn.delete_synsetdef('にゃんこ大戦争')
    wordnetdb_test_print(wn, 'ネコ')

    wn.add_word('アリス')
    wn.add_synlink('アリス', 'n', 'アリスの不思議な国', 'n', '主人公')
    wordnetdb_test_print(wn, 'アリス')

    wn.delete_word('アリス')
    wordnetdb_test_print(wn, 'アリス')

# wordnetdb_test()

# wn = WordNetDb()
# result = wn.get_imagenet_uris('アリス')
# print(result)

# cur = wn.get_synlink_info_by_name('true_cat')
# for w in cur:
#     print(w)

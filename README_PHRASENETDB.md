# PhraseNetDb

フレーズとスキーマの定義と関連付けの定義を持つDBアクセスライブラリ

## Install

```
pip install git+https://github.com/hiraokusky/snark
```

日本語WordNetのsqlite3データベースをダウンロードし、db/wnjpn.dbに置きます。
http://compling.hss.ntu.edu.sg/wnja/jpn/index.html

スクリプトで以下のimportを書きます。

```
from snark import phrasedb
```

## フレーズとスキーマ

フレーズは、語を組み合わせて構成した句に相当しますが、ここではもう少し大きな範囲も扱います。
https://ja.wikipedia.org/wiki/%E5%8F%A5

スキーマは、イメージスキーマに相当するものを言語やオブジェクトとして記述したものです。
ここでは、演算可能なイメージスキーマとして定義しています。

フレーズには、スキーマが対応しています。
この情報によって、フレーズに対する演算が可能になります。
例えば、ワードネットのスキーマは、イメージネットの画像になります。

フレーズネットは、これらの情報を用いて、文章とイメージスキーマの変換をするためのデータを蓄積・利用する環境を提供することを目指しています。

## フレーズの種類

r

主に文の始めに現れるフレーズ。
接続詞の他、感嘆詞など。

a

対象の名詞を見た心象を相手に伝えるためのフレーズ。

p

名詞に接続するフレーズ。

t

名詞で終わる文、つまり、等価を示す文の終わりに現れるフレーズ。

v

動詞

w

動詞の終わりに現れるフレーズ。

f

会話文の終わりに現れる、人の特徴を示すフレーズ。

## スキーマの定義

深層格との対応

    動作主格 case_agentive
    経験者格 case_experiencer
    道具格 case_instrumental
    対象格 case_objective
    源泉格 case_source
    目標格 case_goal
    場所格 case_locative
    時間格 case_time
    経路格 case_path

## 使い方

### データのロード・セーブ

* load_file

    フレーズデータをファイルからロードする

* load_db

    フレーズデータをWordNetDbからロードする

* save_db

    フレーズデータをWordnetDbにセーブする

### 検索

* get_phrases

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


### ユーティリティ

* get_verb_ends

    get_verb_ends(元の文字列, 動詞原型) -> 元の文字列の動詞活用形部分

* get_adj_ends

    get_adj_ends(元の文字列, 形容詞原型) -> 元の文字列の形容詞活用形部分

# SynNetDb

ワードネットとフレーズネットとRDFを統合するアクセスライブラリ

## Install

```
pip install git+https://github.com/hiraokusky/snark
```

日本語WordNetのsqlite3データベースをダウンロードし、db/wnjpn.dbに置きます。
http://compling.hss.ntu.edu.sg/wnja/jpn/index.html

スクリプトで以下のimportを書きます。

```
from snark import synnetdb
```

## データ構造

RDFと同様のリンク構造を持ちます。
ワードネットとしてはSynLinkと同様の構造を持ちます。

    synset1 link synset2

linkの種類は以下の通りです。

    in   同義
    isa  上位
    hasa 部分
    then 遷移

## 使い方

必要なデータをメモリにロードしてからアクセスします。

### データのロード・セーブ

* load_file

  データをファイルからロードする

* save_file

  データをファイルにセーブする

* load_same_words_from_db

  ワードネットDBから指定の単語のsynsetを共有するwordをinリンクとしてすべてロードする

### 検索

* select

  synsetを取得する

* select_link

  リンク先の全synsetを取得する

* select_link_ref

  リンク元の全synsetを取得する

* select_isa

  isaリンクとinリンクを持つ全synsetを取得する

* select_same

  keyと同じinを持つ全synsetを取得する

* add_link

  リンクを追加する

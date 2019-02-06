# snark

日本語ワードネットを基本とした各種DBにアクセスするためのライブラリです。
それぞれのライブラリは基本的に独立して利用することができます。

## Install

```
pip install git+https://github.com/hiraokusky/snark
```

日本語WordNetのsqlite3データベースをダウンロードし、db/wnjpn.dbに置きます。
http://compling.hss.ntu.edu.sg/wnja/jpn/index.html

## WordNetDb

日本語ワードネットを利用したDBアクセスライブラリ

[README](README_WORDNETDB.md)

## KanaDb

簡単な仮名の処理を行うライブラリ

## PhraseNetDb

フレーズとスキーマの定義と関連付けの定義を持つDBアクセスライブラリ

[README](README_PHRASENETDB.md)

## SynNetDb

ワードネットとフレーズネットとRDFを統合するアクセスライブラリ

[README](README_SYNNETDB.md)

## WebReader

Webコンテンツへのアクセスライブラリ

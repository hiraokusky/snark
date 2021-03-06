# WordNetDb

日本語ワードネットを利用したDBアクセスライブラリ

## Install

```
pip install git+https://github.com/hiraokusky/snark
```

日本語WordNetのsqlite3データベースをダウンロードし、db/wnjpn.dbに置きます。
http://compling.hss.ntu.edu.sg/wnja/jpn/index.html

スクリプトで以下のimportを書きます。

```
from snark import wordnetdb
```

## 使い方

### WordNetDbオブジェクトを取得する

```
wn = wordnetdb.WordNetDb()
```

### DBに単語を追加する
wn.add_word(単語, 概念ID)

* 概念IDは省略可能

```
wn.add_word('にゃんこ', 'true_cat')
```

### DBから単語と一致するワードを取得する
ワードオブジェクトリスト = wn.get_words(単語)

### 概念の例文を取得する
概念オブジェクトリスト = wn.get_synsets(ワードオブジェクト)

### 概念の例文を取得する
例文オブジェクトリスト = wn.get_synsetdefs(概念オブジェクト)

### 概念に紐づく単語のリストを取得する
ワードオブジェクトリスト = wn.get_words_by_sense(概念オブジェクト)

### 概念の例文と紐づく単語のリストを取得する
リスト = wn.get_synset_info(概念オブジェクト)

リストの形式:
* [親概念ID, 種類, ID, 名前, 品詞ID, 例文]

種類:
* synset: 概念オブジェクト
* word: 概念を示すワードオブジェクト

```
['', 'synset', '02121620-n', 'true_cat', 'n', '通常、厚く柔らかい毛皮を持ち、吠えることのできないネコ科の哺乳類：家ネコ,ヤマネコ']
['02121620-n', 'word', 57508, 'true_cat', 'n']
['02121620-n', 'word', 97864, 'cat', 'n']
['02121620-n', 'word', 181396, 'ねんねこ', 'n']
['02121620-n', 'word', 186221, 'にゃんにゃん', 'n']
['02121620-n', 'word', 186873, '猫', 'n']
['02121620-n', 'word', 204434, 'キャット', 'n']
['02121620-n', 'word', 208204, 'ネコ', 'n']
```

### 概念に関連する概念の単語のリストを取得する
リスト = wn.get_synlink_info(概念オブジェクト)

リストの形式:
* [親概念ID, 種類, ID, 名前, 品詞ID, 例文]

種類:
* (リンクID): 関係する概念の情報
* synset: 関係する概念オブジェクト
* word: 関係する概念を示すワードオブジェクト

```
['02121620-n', 'hype', '02120997-n', 'feline', 'n']
['02121620-n', 'synset', '02120997-n', 'feline', 'n', 'しなやかな体で頭の丸い様々な裂脚類の哺乳動物で、多くは引っ込める ことのできる鉤爪を持つ']
['02120997-n', 'word', 88, 'feline', 'n']
['02120997-n', 'word', 79279, 'felid', 'n']
['02121620-n', 'hypo', '02121808-n', 'house_cat', 'n']
['02121620-n', 'synset', '02121808-n', 'house_cat', 'n', 'ネコ属の飼い慣らされた各種の猫']
['02121808-n', 'word', 8342, 'house_cat', 'n']
['02121808-n', 'word', 59132, 'felis_catus', 'n']
['02121808-n', 'word', 67584, 'domestic_cat', 'n']
['02121808-n', 'word', 90633, 'felis_domesticus', 'n']
['02121808-n', 'word', 220428, '飼い猫', 'n']
['02121620-n', 'hypo', '02124623-n', 'wildcat', 'n']
['02121620-n', 'synset', '02124623-n', 'wildcat', 'n', 'イエネコに似た野生の小型または中型猫']
['02124623-n', 'word', 47529, 'wildcat', 'n']
['02124623-n', 'word', 212854, '山猫', 'n']
```

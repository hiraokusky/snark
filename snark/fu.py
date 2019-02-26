
# 名もないライブラリ

def match(a, s, sep=','):
    """
    aとsをゆるく比較する
    sは,区切りの集合を与えることができる
    """
    c = s.split(sep)
    for b in c:
        if a == b or a in b or b in a:
            return True
    return False

def array2_to_str(a, i,sep=','):
    """
    2次元配列の各行のi番目のデータを,つなぎの文字列にする
    """
    s = list(map(lambda x: x[i], a))
    s = sep.join(s)
    return s

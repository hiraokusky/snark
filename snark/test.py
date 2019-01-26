from webreader import WebReader
from bs4 import BeautifulSoup

# 文の解析を開始する
wr = WebReader()
page = wr.get_web_page('https://www.msdmanuals.com/ja-jp/%E3%83%97%E3%83%AD%E3%83%95%E3%82%A7%E3%83%83%E3%82%B7%E3%83%A7%E3%83%8A%E3%83%AB/12-%E5%85%8D%E7%96%AB%E5%AD%A6%EF%BC%9B%E3%82%A2%E3%83%AC%E3%83%AB%E3%82%AE%E3%83%BC%E7%96%BE%E6%82%A3/%E5%85%8D%E7%96%AB%E4%B8%8D%E5%85%A8%E7%96%BE%E6%82%A3/%E5%85%8D%E7%96%AB%E4%B8%8D%E5%85%A8%E7%96%BE%E6%82%A3%E3%81%AE%E6%A6%82%E8%A6%81')
content = page.select_one("div.body.topic-content")

while True:
    content = content.find_next(['h1','h2','h3','h4','p'])
    if '<h' in content.text:
        print('')
        print('')
    print(content.text)
    if '要点' in content:
        break

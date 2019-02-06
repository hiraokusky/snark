"""
Copyright 2019 hiraokusky

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
import re
import urllib.parse

# pip install beautifulsoup4
from bs4 import BeautifulSoup

# pip install selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# pip install rdflib
import rdflib

class WebReader:
    """
    Webから情報を取得する
    """

    # Chrome WebDriverが必要
    # @see https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.chrome.webdriver
    driver = None

    rdf_graph = rdflib.Graph()

    cache_path = ''

    def __init__(self):
        options = Options()
        options.set_headless(True)
        self.driver = webdriver.Chrome(chrome_options=options)

    def use_cache(self, path):
        self.cache_path = path

    def get_web_page(self, url):
        """
        Webページを取得してBeautifulSoupオブジェクトにする
        """
        if len(self.cache_path) > 0:
            # urlをencodeしたファイル名があればそれを返す
            return

        self.driver.get(url)
        html = self.driver.page_source.encode('utf-8')

        if len(self.cache_path) > 0:
            # urlをencodeしてファイルに保存する
            return

        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_rdf(self, url):
        """
        RDFを取得する
        """
        self.rdf_graph.load(url)
        return self.rdf_graph

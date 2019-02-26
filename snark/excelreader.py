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
import pandas as pd
import sqlite3


class ExcelReader:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def __enter__(self):
        return self

    def __del__(self):
        self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def load_excel(self, name):
        """
        ExcelファイルからDBを作成する
        Excelファイルのシート1の各列が別々のテーブルになる
        indexは共通の番号になる
        """
        dfs = pd.read_excel(name, sheet_name=0)

        for table, df in dfs.items():
            df.to_sql(table, self.conn)

        return dfs

    def save_excel(self, name, df):
        df.to_excel(name)

    def select(self, targets, tables, wheres):
        """
        Excelファイルから作成したDBを検索する
        Parameters
        ----------
        targets : array
            出力対象のテーブル名(列名も同値である必要あり)
        tables : array
            検索対象のテーブル名
        wheres : array
            テーブルごとの検索文字列
        Examples
        --------
        cur = db.select(['医療機関名', '郵便番号'], ['都道府県', '病院機能'], ['t1."都道府県"="沖縄県"', 't2."病院機能"=3'])
        """
        sql = 'select d1."index",'
        i = 1
        for target in targets:
            if i > 1:
                sql += ','
            sql += 'd' + str(i) + '."' + target + '"'
            i += 1
        sql += ' from '
        i = 1
        for table in tables:
            if i > 1:
                sql += ','
            sql += '"' + table + '" as t' + str(i)
            i += 1
        i = 1
        for target in targets:
            sql += ','
            sql += '"' + target + '" as d' + str(i)
            i += 1
        sql += ' where ('
        i = 1
        for where in wheres:
            if i > 1:
                sql += ' and t' + str(i - 1) + \
                    '."index" = t' + str(i) + '."index" and '
            sql += where
            i += 1
        i = 1
        for target in targets:
            sql += ' and t1."index" = d' + str(i) + '."index" '
            i += 1
        sql += ');'
        # print(sql)
        cur = self.conn.execute(sql)
        return cur

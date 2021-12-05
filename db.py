import os
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

USER = 'root'
PASSWORD = 'aaaa'
HOST = '127.0.0.1'
DATABASE = 'azdb'

engine=create_engine(f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}')
Base = declarative_base()
Session=sessionmaker(engine)
session=Session()

def get_keyword():
    # MySQL Connector/Pythonを使うためmysqlconnectorを指定する

    keyword_list = []
    asin_list = []

    class Az(Base):
        __tablename__ = 'keyword_ranking_requests'
        id = Column(String, primary_key=True)
        asin = Column(String)
        keyword = Column(String)

    for r in session.query(Az):
        keyword_list.append(r.keyword)
        asin_list.append(r.asin)

    return keyword_list, asin_list

def insert_data(asin_value, keyword_value, ranking_value): 
    class Keyword_ranking(Base):
        __tablename__ = 'keyword_ranking'
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
        asin = Column(String)
        keyword = Column(String)
        ranking = Column(Integer)
        ymd = Column(Integer)
        updated_at = Column(String)
        created_at = Column(String)
        
  
    # tmp = Keyword_ranking(id=id_value, asin=asin_value, keyword=keyword_value, ranking=ranking_value, ymd="20211205", updated_at="20211205", created_at="20211205")
    tmp = Keyword_ranking(asin=asin_value, keyword=keyword_value, ranking=ranking_value, ymd="20211205", updated_at="20211205", created_at="20211205")

    session.add(tmp)
    session.commit()


def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
          options = ChromeOptions()
    else:
      options = Options()

    # ヘッドレスモード（画面非表示モード）を設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

def search_az():
    # driverを起動
    ids = 0
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    keywords, asins = get_keyword()
    
    for keyword, asin in zip(keywords, asins):

        ids = ids + 1
        # Webサイトを開く
        driver.get("https://www.amazon.co.jp/")
        time.sleep(1)
        
        
        search_bar = driver.find_element_by_name("field-keywords")
        search_bar.send_keys(keyword)
        driver.find_element_by_css_selector("#nav-search-submit-button").click()


        product_num = 0
        # global product_list
        # product_list = []
        
        df = pd.DataFrame()
        
        while product_num <= 300:
            elements = driver.find_elements_by_css_selector(".a-size-mini.a-spacing-none.a-color-base.s-line-clamp-4 > a")
            product_num = len(elements) + product_num


            for element in elements:
                # DataFrameに対して辞書形式でデータを追加する
                d = {"URL": element.get_attribute("href")}
                df = df.append(d, ignore_index=True)
                

            try:
            #ページ切り替え処理
                next_page_url = driver.find_element_by_css_selector(".a-last > a").get_attribute("href")

                driver.get(next_page_url)
                df.to_csv('to_csv_out.csv', mode="w")
                time.sleep(1)
            except:
                print("ページなし、終了")
                break               


        print(df[df['URL'].str.contains(asin)])

        ranking = df.index.values.tolist()
       
        print(ranking)
        if ranking == 0:
            insert_data(asin, keyword, ranking[0])   
        else:
            ranking[0] = 0
            insert_data(asin, keyword, ranking[0])   

            


               
# # 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    search_az()
    
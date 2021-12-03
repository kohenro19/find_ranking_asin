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
PASSWORD = 'xxxxxxxxxx'
HOST = '127.0.0.1'
DATABASE = 'azdb'

def get_keyword():
    # MySQL Connector/Pythonを使うためmysqlconnectorを指定する
    engine=create_engine(f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}')

    Base = declarative_base()

    class Az(Base):
        __tablename__ = 'keyword_ranking_requests'
        id = Column(String, primary_key=True)
        # name = Column(String)
        # birthday = Column(String)
        # address = Column(String)
        # deptcode = Column(String)
        keyword = Column(String)
        
    Session=sessionmaker(engine)
    session=Session()

    keyword_list = []
    for r in session.query(Az):
        keyword_list.append(r.keyword)


    return keyword_list

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
    
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)


    
    keywords = get_keyword()
    
    for keyword in keywords:
        # Webサイトを開く
        driver.get("https://www.amazon.co.jp/")
        time.sleep(1)
        
        
        search_bar = driver.find_element_by_name("field-keywords")
        search_bar.send_keys(keyword)
        driver.find_element_by_css_selector("#nav-search-submit-button").click()


        product_num = 0
        global product_list
        product_list = []
        
        df = pd.DataFrame()
        
        while product_num <= 300:
            elements = driver.find_elements_by_css_selector(".a-size-mini.a-spacing-none.a-color-base.s-line-clamp-4 > a")
            product_num = len(elements) + product_num


            for element in elements:
                # DataFrameに対して辞書形式でデータを追加する
                d = {"URL": element.get_attribute("href")}
                df = df.append(d, ignore_index=True)
                
            # step to the next page
            next_page_url = driver.find_element_by_css_selector(".a-last > a").get_attribute("href")
            if not next_page_url == '':
                break
                
            driver.get(next_page_url)
            time.sleep(1)

            df.to_csv('to_csv_out.csv', mode="a")
        # print(df.URL)
        
        # df = df[df['URL'].str.contains()]
        # ansi_line = df.index.values.tolist()

                


# # 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    search_az()

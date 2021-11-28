import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import session, sessionmaker
 

def con_sql():
    engine = sqlalchemy.create_engine('sqlite:///sample_db.sqlite3', echo=True)
    Base = declarative_base()
    

    class Fruit(Base):
        __tablename__ = 'fruit'

        id = Column(Integer, primary_key=True)
        name = Column(String(length=255))



    Base.metadata.create_all(engine)
    
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    
    # p1 = Fruit(name='Banana')
    # session.add(p1)
    # session.commit()
    
    query_result = session.query(Fruit)
    for fruit in query_result:
        print(fruit.name)
    
# Chromeを起動する関数
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


    
def search_az(asni):
    # driverを起動
    
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    # Webサイトを開く
    driver.get("https://www.amazon.co.jp/")
    time.sleep(5)
    
    
    search_bar = driver.find_element_by_name("field-keywords")
    search_bar.send_keys(asni)
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
        driver.get(next_page_url)


    df.to_csv('to_csv_out.csv', mode="a")
    print(df.URL)
            
    time.sleep(5)
        
    driver.close

 

# # 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
     search_az("イヤホン")
    #  con_sql()
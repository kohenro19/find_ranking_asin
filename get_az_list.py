import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import sqlite3

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
# main処理
def read_csv():
    pass

def write_csv():
    pass
    
def search_word(asni):
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
    while product_num <= 300:
        elements = driver.find_elements_by_css_selector(".a-size-mini.a-spacing-none.a-color-base.s-line-clamp-4 > a")
        product_num = len(elements) + product_num

        for element in elements:
            print(element.get_attribute("href"))
        
        next_page_url = driver.find_element_by_css_selector(".a-last > a").get_attribute("href")

        driver.get(next_page_url)
        time.sleep(5)

 

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
     search_word("イヤホン")
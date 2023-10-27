import time
import pymysql #資料庫套件
from selenium import webdriver
import chromedriver_autoinstaller
from bs4 import BeautifulSoup

def connect_db(host, user, pwd, dbname, port):
    try:
        db = pymysql.connect(
            host = host,
            user = user,
            passwd = pwd,
            database = dbname,
            port = int(port)
        )
        # print("連線成功")
        return db
    except Exception as e:
        print('連線資料庫失敗: {}'.format(str(e)))
    return None


def getUSD(url):
    try:
        # chromedriver_autoinstaller.install() # 115版本有問題
        option = webdriver.ChromeOptions()
        # 【參考】https://ithelp.ithome.com.tw/articles/10244446
        option.add_argument("headless") # 不開網頁搜尋
        option.add_argument('blink-settings=imagesEnabled=false') # 不加載圖片提高效率
        option.add_argument('--log-level=3') # 這個option可以讓你跟headless時網頁端的console.log說掰掰
        """下面參數能提升爬蟲穩定性"""
        option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
        option.add_argument('--disable-gpu') # 規避部分chrome gpu bug

        driver = webdriver.Chrome(chromedriver_path, chrome_options=option) #啟動模擬瀏覽器
        # driver = webdriver.Chrome(chrome_options=option) #啟動模擬瀏覽器
        driver.get(url)

        if not driver.title:
            print(f"📛未成功進入頁面...")
            pass
        
        print(f"✅成功進入頁面...({driver.title})")

        time.sleep(3) # 避免還沒進入頁面就在抓資料

        soup = BeautifulSoup(driver.page_source,'html.parser')
        _date = soup.select('#ie11andabove > div > p.text-info')[0].getText().strip() # 掛牌時間

        # td:nth-child(n)
        # n = 2 (現金-本行買入)     
        # n = 3 (現金-本行賣出	)     
        # n = 4 (即期-本行買入)     
        # n = 5 (即期-本行賣出)     
        usd_price = soup.select('#ie11andabove > div > table > tbody > tr:nth-child(1) > td:nth-child(5)')[0].get_text()
        print(_date)
        print(f"即期-本行賣出: {usd_price}")
        return usd_price
    except KeyboardInterrupt:
        print("----(已中斷程式)----")

    except Exception as e:
        print(f"捕捉資料發生錯誤: {e}")
        return None
    
    finally: # 最終都會關閉 chromedriver
        driver.close()
        driver.quit()

    



if __name__ == "__main__":
    chromedriver_path = './chromedriver.exe'
    url = 'https://rate.bot.com.tw/xrt/all/day'
    db = connect_db('127.0.0.1', 'root', 'Ru,6e.4vu4wj/3', 'greenhouse', 3306) # 資料庫連線
    if( not db ):
        print("資料庫連線發生問題")

    try:
        usd_price = getUSD(url)

        if usd_price:
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE usdollars SET USD = %s WHERE id = 1",
                    (usd_price)
                )
                db.commit()
    except Exception as e:
        print(f"發生錯誤: {e}")



    print("程式執行結束，3秒後將關閉")
    time.sleep(3)
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


"""讀取檔案"""
def read_SQL():
    path = '../sql.txt'
    config = dict() # 資料庫設定
    f = None
    try:
        with open(path, 'r', encoding="utf8") as f: # 讀取 JSON檔案
            lines = f.readlines()
            for line in lines:
                s = line.split('=')
                key = s[0]
                val = s[1]
                val = val.replace("\n", "").strip() # 因為有換行符號，因此要做取代
                config[key] = val
    except IOError:
        print('ERROR: can not found ' + path)
    finally:
        if f:
            f.close()
        return config

if __name__ == "__main__":
    # chromedriver_autoinstaller.install() # 115版本有問題
    option = webdriver.ChromeOptions()
    # 【參考】https://ithelp.ithome.com.tw/articles/10244446
    option.add_argument("headless") # 不開網頁搜尋
    option.add_argument('blink-settings=imagesEnabled=false') # 不加載圖片提高效率
    option.add_argument('--log-level=3') # 這個option可以讓你跟headless時網頁端的console.log說掰掰
    """下面參數能提升爬蟲穩定性"""
    option.add_argument('--disable-dev-shm-usage') # 使用共享內存RAM
    option.add_argument('--disable-gpu') # 規避部分chrome gpu bug

    driver = webdriver.Chrome("./chromedriver.exe", chrome_options=option) #啟動模擬瀏覽器
    # driver = webdriver.Chrome(chrome_options=option) #啟動模擬瀏覽器
    driver.get('https://rate.bot.com.tw/xrt/all/day')

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
    print(usd_price)

    # db = connect_db()
    config = read_SQL()
    db = connect_db('127.0.0.1', 'root', 'Ru,6e.4vu4wj/3', 'greenhouse', 3306) # 資料庫連線

    if( not db ):
        print("資料庫連線發生問題")

    cursor = db.cursor()


    sql = f"UPDATE usdollars SET USD = {usd_price} WHERE id = 1"
    cursor.execute(sql)
    db.commit()


    driver.close()
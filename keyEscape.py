from selenium import webdriver
import csv
import time
from datecal import reserve_date_list_hyphen
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pymysql

def crawling(days,trial_time):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='asdf1234', db='roomescape', charset='utf8')
    cursor = db.cursor()
    datelist = reserve_date_list_hyphen(days)
    url = 'https://keyescape.co.kr/web/home.php?go=rev.make'

    # 1. 처음에는 밑의 한줄로 크롬 드라이버 매니저 설치하고 돌리는 것을 추천
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # 2. 크롬 드라이버 매니저 설치 후에는 절대경로 따서 돌리는 게 낫습니다.
    # driver = webdriver.Chrome('C:/Program Files/driver/chromedriver.exe')

    # 3. 헤드리스로 돌리는 경우 아래 5줄 실행하기. 경로는 수정해서.
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome('C:/Program Files/driver/chromedriver.exe', options=options)

    driver.get(url)
    storesul = driver.find_element_by_xpath('//*[@id="zizum_data"]')
    storeslist = storesul.find_elements_by_tag_name("a")
    for store in storeslist:
        store_name = "키이스케이프 " + store.text
        store_script = store.get_attribute("href")
        driver.execute_script(store_script)
        time.sleep(0.5)
        for date in datelist:
            driver.execute_script("javascript:fun_days_select('%s','0');"%date)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'theme_data')))
            questsul = driver.find_element_by_xpath('//*[@id="theme_data"]')
            questslist = questsul.find_elements_by_tag_name("a")
            time.sleep(1)
            for questidx in range(len(questslist)):
                now = time.localtime()
                s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'a')))
                    quest = driver.find_element_by_xpath('//*[@id="theme_data"]/a[%s]'%(questidx+1))
                    quest_name = quest.text
                    quest_script = quest.get_attribute("href")
                    driver.execute_script(quest_script)
                    time.sleep(1)
                except:
                    pass
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'theme_time_data')))
                time.sleep(1)
                timesul=driver.find_element_by_xpath('//*[@id="theme_time_data"]')
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'li')))
                timesli=timesul.find_elements_by_tag_name("li")
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.TAG_NAME, 'li')))
                for reserve_time in timesli:
                    time.sleep(0.1)
                    if(reserve_time.get_attribute("class")=="impossible"):
                        reservation_available = False
                    else:
                        reservation_available = True
                    quest_time = reserve_time.text
                    sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                          "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                          trial_time, s, date, store_name, quest_name, quest_time, reservation_available)
                    cursor.execute(sql)

    db.commit()
    db.close()

# crawling(2,"2020-03-29 13:11")
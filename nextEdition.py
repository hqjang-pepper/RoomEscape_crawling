from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import pymysql
import time
import datetime
from datecal import reserve_date_list_hyphen

def crawling(days,trial_time):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='asdf1234', db='roomescape', charset='utf8')
    cursor = db.cursor()
    date_list = reserve_date_list_hyphen(days)
    url = 'https://www.nextedition.co.kr/'

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
    driver.find_element_by_xpath('//*[@id="navbarNavDropdown"]/ul/li[2]/a').click()
    dropdownul = driver.find_element_by_xpath('//*[@id="navbarNavDropdown"]/ul/li[2]/ul')
    shopslink = dropdownul.find_elements_by_tag_name("a")
    shops_url_list = []
    for shop in shopslink:
        alpha = shop.get_attribute("href")
        shops_url_list.append(alpha)

    #각 가게별 링크를 타고 들어가는데까지 성공
    for i in range(len(shops_url_list)-1):
        driver.get(shops_url_list[i])
        store_name = driver.find_element_by_tag_name('h1').text
        datepicker = driver.find_element_by_xpath('//*[@id="datepicker"]')
        for date in date_list:
            datepicker.clear()
            datepicker.send_keys(date)
            datepicker.send_keys(Keys.ENTER)
            datepicker.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)
            questlist = driver.find_elements_by_class_name("row")
            for i in range(1, int((len(questlist)) / 2)):
                try:
                    quest_info_div = driver.find_element_by_xpath('//*[@id="%s"]/div[%s]/div/div/div[2]' % (date, i))
                    quest_name = quest_info_div.find_element_by_tag_name("h2").text
                    timeinfo_list = quest_info_div.find_elements_by_tag_name("div")
                    now = time.localtime()
                    s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                    for timeinfo in timeinfo_list:
                        time_id = timeinfo.get_attribute("id")
                        quest_time = driver.find_element_by_xpath('//*[@id="%s"]/span[1]' % time_id).text
                        reservation_available = driver.find_element_by_xpath('//*[@id="%s"]/span[2]' % time_id).text
                        if(reservation_available=="예약가능"):
                            reservation_available = True
                        else:
                            reservation_available = False
                        sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                              "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                                  trial_time, s, date, store_name, quest_name, quest_time, reservation_available)
                        cursor.execute(sql)
                except:
                    pass
    db.commit()
    db.close()

# crawling(2,"2020-03-29 13:11")

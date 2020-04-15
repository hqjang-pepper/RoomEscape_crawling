from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datecal import reserve_date_list_hyphen
import csv
import time
import datetime
import pymysql

def crawling(days,trial_time):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='asdf1234', db='roomescape', charset='utf8')
    cursor = db.cursor()

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

    url = 'http://www.master-key.co.kr/home/office'
    driver.get(url)
    escape_view_li = driver.find_elements_by_class_name("escape_view")
    datelist = reserve_date_list_hyphen(days)
    bid_list=[]
    #각 스토어에 해당하는 id를 얻어내기 위해서.
    for li in escape_view_li:
        bid_list.append(li.get_attribute("id")[7:])
    for bid in bid_list: # 각 스토어별로 접근
        store_url = 'http://www.master-key.co.kr/booking/bk_detail?bid='+bid
        driver.get(store_url)
        store_name = "마스터키 "+ driver.find_element_by_tag_name("h2").text


        for date in datelist: # 각 날짜별로 접근
            datepicker = driver.find_element_by_xpath('//*[@id="dates"]')
            datepicker.clear()
            datepicker.send_keys(date)
            datepicker.send_keys(Keys.ENTER) #여기까지 했으면 날짜가 바뀐거임. 이제 본격적인 퀘스트 및 시간 크롤링
            #날짜를 바꾸고 기다리는 시간 최소 3초 필요
            time.sleep(3)
            escape_infos = driver.find_elements_by_class_name("res_box_wrap")
            #퀘스트별로 접근
            for quest in escape_infos:
                #안하면 에러남
                driver.implicitly_wait(5)
                quest_name = quest.find_elements_by_tag_name("p")[0].text
                times = quest.find_elements_by_class_name("time")
                reservation_availables = quest.find_elements_by_class_name("state")
                now = time.localtime()
                s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                #퀘스트별로 잠깐 시간이필요할때도 있음
                driver.implicitly_wait(1)
                #퀘스트 시간별로 접근
                for i in range(len(times)):
                    if(reservation_availables[i].text=="예약가능"):
                        sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                              "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                              trial_time, s, date, store_name, quest_name, times[i].text, True)
                        cursor.execute(sql)
                    else:
                        sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                              "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                                  trial_time, s, date, store_name, quest_name, times[i].text, False)
                        cursor.execute(sql)

    db.commit()
    db.close()

# crawling(2,"2020-03-29 13:11")
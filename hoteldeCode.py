from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pymysql
import csv
import time
from datecal import reserve_date_list_hyphen

def crawling(days,trial_time):
    db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='asdf1234',db='roomescape',charset='utf8')
    cursor = db.cursor()
    datelist = reserve_date_list_hyphen(days)

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

    for date in datelist:
        #날짜별로 url을 만들어 접근하는 것이 호텔드 코드에서는 가능.
        url = 'http://hoteldecode.com/reservation/reservation.php?date='+date
        driver.get(url)
        #사이트 로딩까지 기다려줌.
        driver.implicitly_wait(5)
        quests = driver.find_elements_by_xpath("//div[contains(@class, 'row mt40')]")
        #각 퀘스트별로 접근
        for quest in quests:
            now = time.localtime()
            s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

            quest_name = quest.find_element_by_tag_name('h4').text
            timebox = quest.find_element_by_xpath("//div[contains(@class, 'time_box')]")
            times = timebox.find_elements_by_tag_name("div")
            #시간과 '예약가능 또는 예약불가'를 나눠야함.
            for quest_time in times:
                quest_time,reservation_available = quest_time.text.split()
                if(reservation_available=='예약가능'):
                    reservation_available = True
                else:
                    reservation_available = False
                sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                      "VALUES ('%s','%s','%s','%s','%s','%s',%s)"%(trial_time,s,date,'호텔드코드',quest_name,quest_time,reservation_available)
                cursor.execute(sql)
    db.commit()
    db.close()
# crawling(2,"2020-03-29 13:11")
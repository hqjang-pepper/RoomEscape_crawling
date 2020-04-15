from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datecal import day_list , reserve_date_list_hyphen
import pymysql
import csv
import time
import datetime

def crawling(days,trial_time):
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='asdf1234', db='roomescape', charset='utf8')
    cursor = db.cursor()
    daylist = day_list(days)
    datelist = reserve_date_list_hyphen(days)
    url = "https://www.seoul-escape.com/reservation/"
    # 1. 처음에는 밑의 한줄로 크롬 드라이버 매니저 설치하고 돌리는 것을 추천
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # 2. 크롬 드라이버 매니저 설치 후에는 절대경로 따서 돌리는 게 낫습니다.
    driver = webdriver.Chrome('C:/Program Files/driver/chromedriver.exe')

    # 3. 헤드리스로 돌리는 경우 아래 5줄 실행하기. 경로는 수정해서.
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument("disable-gpu")
    # driver = webdriver.Chrome('C:/Program Files/driver/chromedriver.exe', options=options)

    driver.get(url)
    for daylist_index in range(len(daylist)):
        # print(daylist[daylist_index])
        # print('program should click' + str(daylist[daylist_index]))
        date_button = driver.find_element_by_xpath('//*[@id="reserve_date"]')
        date_button.click()
        tbody = driver.find_element_by_xpath('/html/body/div[4]/div[1]/table/tbody')
        days = tbody.find_elements_by_tag_name("td")
        time.sleep(3)
        # print(days)
        for day in days:
            if(daylist_index==0): #첫날은 달력 누르는거 패스. 이거하니까 첫날은 잘 작동됨.
                break
            else:
                if (day.get_attribute("class")=="day old disabled" or day.get_attribute("class")=="day disabled"):
                    continue
                else:
                    time.sleep(0.1)
                    # if(day.text == str(daylist[daylist_index])):
                    if(day.text ==str(daylist[daylist_index])):
                        # print('program will click',day.text)
                        day.click()
                        break
        #날 클릭 후 로딩까지 3초는 기다려줘야 합니다.
        time.sleep(3)
        for i in range(6): #스토어 6개
            driver.implicitly_wait(3)
            #가게별로 접근합니다.
            driver.find_element_by_xpath('//*[@id="branchMenu"]').click()
            dropdown_menu = driver.find_element_by_xpath(
                '//*[@id="book_a_session_wrapper"]/div[1]/div[1]/div/div[2]/div/ul')
            storesli = dropdown_menu.find_elements_by_tag_name('a')
            storesli[i].click()
            # 날짜 선택하는 로직 여기에다가 구현해야함!!

            tablebody = driver.find_element_by_xpath('//*[@id="book_a_session_wrapper"]/table/tbody')
            tablerowlist = tablebody.find_elements_by_tag_name('tr')
            # 후에 sql에 쓸 가게 이름을 뽑아내기 위한 코드입니다.

            store_name = '서울 이스케이프룸 ' + driver.find_element_by_xpath(
                '//*[@id="book_a_session_wrapper"]/table/tbody/tr[2]/td[1]').text
            #퀘스트별로 접근.
            for j in range(2, len(tablerowlist) + 1):
                #퀘스트이름,시간 및 예약확인
                now = time.localtime()
                s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                #표의 시작시간, 퀘스트 이름, 예약가능여부가 2번째줄 4번째줄 8번째 줄에 있으므로 그걸 가져옴.
                start_time = driver.find_element_by_xpath(
                    '//*[@id="book_a_session_wrapper"]/table/tbody/tr[%s]/td[2]' % j).text
                quest_name = driver.find_element_by_xpath(
                    '//*[@id="book_a_session_wrapper"]/table/tbody/tr[%s]/td[4]' % j).text
                reservation_available = driver.find_element_by_xpath(
                    '//*[@id="book_a_session_wrapper"]/table/tbody/tr[%s]/td[8]' % j).text
                if reservation_available == "예약하기":
                    reservation_available = True
                else:
                    reservation_available = False
                sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                      "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                          trial_time,s,datelist[daylist_index],store_name,quest_name,start_time,reservation_available)
                cursor.execute(sql)
    db.commit()
    db.close()

crawling(2,"2020-03-31 13:11")
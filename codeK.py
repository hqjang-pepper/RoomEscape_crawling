from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import pymysql
from datecal import reserve_date_list_hyphen

def crawling(days,trial_time):

    storelist=['S1','S2','S3']
    datelist = reserve_date_list_hyphen(days)
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

    driver.implicitly_wait(5)
    thema_id_count = 0

    #가게가 단 3곳밖에 없어서 이렇게 직접 하드코딩했습니다.
    for store in storelist:
        if(store=='S1'):
            store_name = "코드케이 강남점"
        elif(store=='S2'):
            store_name = "코드케이 구월점"
        elif (store=='S3'):
            store_name = "코드케이 홍대점"

        thema_id_count += 1
        thema_id = "thema"+str(thema_id_count)
        for date in datelist:
            #가게와 날짜를 가지고 직접 url에 접근
            url = "http://www.code-k.co.kr/sub/code_sub04_1.html?R_JIJEM=%s&R_THEMA=&CHOIS_DATE=%s&DIS_T=A" %(store,date)
            driver.get(url)
            #테마아이디를 가지고 퀘스트리스트를 리턴받음
            questlist = driver.find_elements_by_class_name(thema_id)
            id_count=0
            for quest in questlist:
                quest.click()
                id_count+=1
                #퀘스트아이디를 1씩 증가시키면서 순차적으로 시간및 예약여부를 가져옴
                CQid = "CQ"+str(id_count)
                timeul = driver.find_element_by_id(CQid)
                timesli = timeul.find_elements_by_tag_name("li")
                now = time.localtime()
                s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                #timeoff일땐 예약불가, timeon일땐 예약가능
                for timeli in timesli:
                    if(timeli.get_attribute("class")=="timeOff"):
                        reserve_avaliable = False
                    elif(timeli.get_attribute("class")=="timeOn"):
                        reserve_avaliable = True

                    reserve_time = timeli.text[2:]

                    sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                          "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                              trial_time, s,date,store_name,quest.text,reserve_time,reserve_avaliable)
                    cursor.execute(sql)
    db.commit()
    db.close()
# crawling(2,"2020-03-29 13:11")
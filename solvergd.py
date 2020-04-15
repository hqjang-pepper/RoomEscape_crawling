from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pymysql
import time
from datecal import day_list

def crawling(days,trial_time):
    daylist = day_list(days)
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

    for i in range(1,3):
        #스토어1 스토어2별로 url 접근
        url = 'http://solver-gd.com/sub/03_1.html?JIJEM=S'+str(i)
        driver.get(url)
        for idx in range(len(daylist)):
            if (idx == 0): #당일이면 패스
                pass
            else: #2일 이후부턴 달력에서 날짜를 클릭해가면서 진행시켜야함. 달력버튼 클릭
                datebutton = driver.find_element_by_xpath('//*[@id="datepicker"]')
                datebutton.click()
                #30일 -> 1일 또는 31일->1일로 넘어가는 것처럼 달이 바뀌는 경우 예외처리 한겁니다.
                if (daylist[idx] < daylist[idx - 1]):
                    #달 넘기는 버튼 클릭
                    driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/div/a[2]/span').click()
                calendar = driver.find_element_by_xpath('//*[@id="ui-datepicker-div"]/table')
                daybuttons = calendar.find_elements_by_tag_name("a")
                for day in daybuttons: #찾고자 하는 날 클릭
                    if (day.text == str(daylist[idx])):
                        day.click()
                        #날을 클릭하고 2초정도의 시간은 최소 기다려야지 프로그램이 돌아갈 수 있다.
                        time.sleep(2)
                        break
            reservation_date = driver.find_element_by_xpath('//*[@id="datepicker"]').get_attribute("value")
            #퀘스트 이름뽑아내기를 별도의 과정으로 해야함.
            questbutton = driver.find_element_by_xpath('//*[@id="sub_content2"]/form/ul/li[1]/select')
            questbutton.click()
            optionslist = questbutton.find_elements_by_tag_name('option')
            quest_name_list = []
            for ops in optionslist:
                quest_name_list.append(ops.text)
            #퀘스트 별로 인덱스를 1씩 증가시키면서 시간을 가져옵니다.
            questdivs = driver.find_elements_by_class_name("reservTime")
            index=0
            for questdiv in questdivs:
                index+=1
                timesul = questdiv.find_element_by_tag_name("ul")
                timesli = timesul.find_elements_by_tag_name("li")
                now = time.localtime()
                s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                for timebox in timesli:
                    quest_time , reservation_available = timebox.text.split("\n")
                    if(reservation_available=="예약가능"):
                        reservation_available = True
                    else:
                        reservation_available = False
                    sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                          "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                              trial_time, s, reservation_date, "건대솔버 "+str(i)+"호점", quest_name_list[index], quest_time, reservation_available)
                    cursor.execute(sql)
    db.commit()
    db.close()
# crawling(2,"2020-03-29 13:11")

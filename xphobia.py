from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datecal import reserve_date_list
from selenium.webdriver.common.by import By

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
import pymysql
import time
import datetime


def crawling(days,trial_time):
    url = "https://www.xphobia.net/reservation/reservation_check.php"
    db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='asdf1234', db='roomescape', charset='utf8')
    cursor = db.cursor()
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
    ymdlist = reserve_date_list(days)
    categoriesul = driver.find_element_by_id('ji_category')
    categoriesli = categoriesul.find_elements_by_tag_name('li')
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

    for i in (2,3,4): # cgv는 뺐습니다. cgv인덱스가 1이어서 1 빼고 234(방탈출 던전 히든퀘스트)
        category = driver.find_element_by_xpath('//*[@id="cate_%s"]/p'%i)

        driver.execute_script("arguments[0].click();", category)
        # driver.implicitly_wait(5)
        storesul=0
        storesli=0
        #가끔 스토어 리스트 불러오는 것도 버벅거릴 때가 있어서 잠깐 기다리게 했습니다. 스토어 리스트 불러오기
        storesul =  WebDriverWait(driver,2,ignored_exceptions=ignored_exceptions)\
                        .until(expected_conditions.presence_of_element_located((By.ID, 'cl1')))
        # driver.implicitly_wait(5)
        storesli = storesul.find_elements_by_tag_name('li')
        # driver.implicitly_wait(5)
        #스토어 클릭
        for store in storesli:


            #아랫줄에서 도대체 왜 staleelementreferenceexception이 일어나는 것인가? 분명히 50초,1초를 기다렸는데도?
            #storesul을 구한 이후에 time.sleep을 해줬더니 문제가 해결되었음.

            driver.execute_script("arguments[0].click();", store)
            try:
                #알람 나오면 기다리기
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert.accept()
            except: #안나올시 패스
                pass
            questsul = driver.find_element_by_id('cl2')
            questsli = questsul.find_elements_by_tag_name('li')
            #퀘스트 리스트 얻어서 퀘스트별로 접근
            for quest in questsli:
                driver.implicitly_wait(5) # 기다리는 명령어 쳤지만 사실 거의 안기다림.
                quest_name = quest.text
                driver.execute_script("arguments[0].click();", quest)
                #역시 기다릴때 가끔있어서 알람 나오면 기다리고 아닌시 패스
                try:
                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                    # shop_name = driver.find_element_by_xpath('//*[@id="f"]/input[1]').get_attribute("value")
                    # quest_name = driver.find_element_by_xpath('//*[@id="f"]/input[2]').get_attribute("value")
                    # quest_name2 = driver.find_element_by_xpath('//*[@id="f"]/input[3]').get_attribute("value")
                    # quest_name2_vis = driver.find_element_by_xpath('//*[@id="f"]/input[4]').get_attribute("value")
                # time.sleep(0.5)
                #후에 jquery를 이용할 때 필요한 파라미터들을 여기서 구해준다.
                shop_name = driver.find_element_by_xpath('//*[@id="f"]/input[1]').get_attribute("value")
                quest_name = driver.find_element_by_xpath('//*[@id="f"]/input[2]').get_attribute("value")
                quest_name2 = driver.find_element_by_xpath('//*[@id="f"]/input[3]').get_attribute("value")
                quest_name2_vis = driver.find_element_by_xpath('//*[@id="f"]/input[4]').get_attribute("value")



                for ymd in ymdlist:
                    #알람이 있을시 기다리기
                    try:
                        WebDriverWait(driver, 3).until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        alert.accept()
                    except: #없을시 바로 jquery 실행
                        driver.execute_script("$('.input_time').val('');")
                        driver.execute_script("$('.input_date').val('%s');" % str(ymd))
                        driver.execute_script("$('.shop_name').val('%s');" % shop_name)
                        driver.execute_script("$('.quest_name').val('%s');" % quest_name)
                        driver.execute_script("$('.quest_name2').val('%s');" % quest_name2)
                        driver.execute_script("reset_ajax();")
                        driver.execute_script("check_date('%s', '%s', '%s', '%s');" % (shop_name, quest_name, str(ymd), quest_name2))
                        timesul = driver.find_element_by_id('cl3')

                        timesli = timesul.find_elements_by_tag_name('li')
                        now = time.localtime()
                        s = "%04d-%02d-%02d %02d:%02d:%02d" % (
                        now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                        for t in timesli:
                            if (t.get_attribute('class') == 'time_lock'):
                                available = False
                            else:
                                available = True
                            sql = "INSERT INTO datatable (code_first_executed_time,crawling_time,roomescape_date,store_name,quest_name,roomescape_time,is_reservation_available) " \
                                  "VALUES ('%s','%s','%s','%s','%s','%s',%s)" % (
                                      trial_time, s, str(ymd), shop_name, quest_name2, t.text, available)
                            cursor.execute(sql)

    db.commit()
    db.close()
# crawling(2,"2020-03-29 13:11")

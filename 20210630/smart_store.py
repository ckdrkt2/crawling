from multiprocessing import Pool
from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd

from re import *
from time import sleep
from time import time


# url 불러오기
url = pd.read_csv("./ss_urls.csv")
url = list(url['0'])

def crawl(url):

    start_time = time()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.implicitly_wait(3)

    # 상품번호 가져오기
    product_No = WebDriverWait(driver,10, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table > tbody > tr:nth-child(1) > td:nth-child(2) > b"))).text
    
    # 리뷰 카테고리 클릭
    categori_css = "#content > div > div.z7cS6-TO7X > div._27jmWaPaKy > ul"
    categoris = WebDriverWait(driver, 10, poll_frequency=0.01).until(lambda x:x.find_element_by_css_selector(categori_css)).text.split('\n')

    # Event 진행중 제거
    if 'Event 진행중' in categoris:
        categoris.remove('Event 진행중')
    # 리뷰 찾아서 클릭
    for i, cat in enumerate(categoris):
        if '리뷰' in cat:
            element = driver.find_element_by_css_selector(categori_css + " > li:nth-child({})".format(str(i+1)))
            break
    # 리뷰가 없으면 종료
    if int(findall('\d+', element.text).pop()) == 0:
        print(product_No, 'no review')
        return
    ActionChains(driver).move_to_element(element).click(element).perform()
    
    # 최신순 클릭
    element = WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > ul > li:nth-child(2)')))
    ActionChains(driver).move_to_element(element).click(element).perform()
    sleep(0.5)

    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])
    

    element = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child(1) > div > div > div > div._1XNnRviOK8 > div > div._1YShY6EQ56 > div._1rZLm75kLm > div._37TlmH3OaI").text

    # 이미지 url 추출
    index = 0
    page = 1
    ex_info = ''
    while True:

        # 페이지 넘어갔는지 체크
        while True:
            page_info = driver.find_element_by_css_selector('#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg').text
            if ex_info != page_info:
                break
        ex_info = page_info

        # 페이지 넘어갈 때 번호 초기화
        num = 1

        while True:
            # 리뷰 정보 추출
            
            try:
                info = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0})".format(str(num))).text
            except:
                break
            
            info_list = list(info.split('\n'))

            # 리뷰 내용 추출
            content = WebDriverWait(driver, 5, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > div > div._1XNnRviOK8 > div > div._1YShY6EQ56 > div._19SE1Dnqkf".format(str(num))))).text
            
            # 좋아요 수 추출
            like = WebDriverWait(driver, 5, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > div > div.fgI31XFKxN".format(str(num))))).text
            
            # 상품옵션 추출
            try:
                product_options = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > div > div._1XNnRviOK8 > div > div._1YShY6EQ56 > div._1rZLm75kLm > div._37TlmH3OaI > div._14FigHP3K8".format(str(num))).text
            except:
                product_options = ''
            
            # 사진 없음
            if '평점' in info_list[0]:
                star  = info_list[1]
                id = info_list[2]
                date = info_list[3]
                img_url = ''
                
            # 사진 있음
            else:
                star  = info_list[2]
                id = info_list[3]
                date = info_list[4]

                # 클릭 되면서 이미지 포함
                if '이미지 펼쳐보기' in info_list:
                    # 더보기 클릭
                    
                    try:
                        more= WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > a".format(str(num)))))
                    except Exception as ex:
                        print(product_No, index, ex); return
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                    sleep(0.1)

                    # 이미지 url 저장
                    try:
                        img = WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > ul".format(str(num)))))
                    except Exception as ex:
                        print(product_No, index, ex)
                    html = img.get_attribute('outerHTML')
                    lst = list(html.split('"'))
                    img_url = list({x.split('?')[0] for x in lst if 'https' in x})
                # 클릭 되면서 이미지 미포함
                else:
                    img_url = ''

            # 데이터프레임에 추가
            df.loc[index] = [id, date, star, product_options, content, like, img_url]

            index += 1
            num += 1
            
        page += 1
        
        # 다음 버튼으로 페이지 넘기기
        next_page = WebDriverWait(driver, 3, poll_frequency=0.05).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > div > div > a:nth-child({0})".format(str(page+1)))))
        if '다음' in next_page.text:
            page = 1
        elif next_page.text == '':
            break
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
    
    driver.close()

    print(product_No, 'runtime:', time() - start_time)

    df.to_csv('lilydress/{}.csv'.format(product_No), encoding='utf-8-sig', mode='w')

if __name__ == '__main__':

    start = time()

    pool = Pool(processes=8)
    pool.map(crawl, url)

    print('total runtime:', time() - start)
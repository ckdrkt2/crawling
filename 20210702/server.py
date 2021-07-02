from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import selenium
import pandas as pd
import parmap

from re import *
from time import time
from time import localtime

# url 불러오기
url = pd.read_csv("/home/ubuntu/workspace/smartstore/urls.csv")
url = list(url['0'])

def crawl(url):
    
    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    start_time = time()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome('/home/ubuntu/workspace/smartstore/chromedriver', chrome_options=options)
    driver.get(url)

    # 상품번호 가져오기
    while True:
        try:
            product_No = driver.find_element_by_css_selector("table > tbody > tr:nth-child(1) > td:nth-child(2) > b").text
            break
        except:
            continue
    print(product_No, 'start')
    
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
        print(product_No, "no review")
        return
    ActionChains(driver).move_to_element(element).click(element).perform()
    
    # 비교를 위한 이전 데이터 저장
    compare = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul").text
    
    # 최신순 클릭
    element = WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > ul > li:nth-child(2)')))
    ActionChains(driver).move_to_element(element).click(element).perform()
    
    # 최신순 버튼이 눌렸으면 통과
    while 'true' != driver.find_element_by_css_selector('#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > ul > li:nth-child(2) > a').get_attribute('aria-checked'):
        print('최신순', product_No, driver.find_element_by_css_selector('#REVIEW > div > div._2y6yIawL6t > div > div._1jXgNbFhaN > div.WiSiiSdHv3 > ul > li:nth-child(2) > a').get_attribute('aria-checked'))
    
    # 이전 데이터와 비교하여 바뀌었으면 통과
    max_wait = time()
    while compare == driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul").text:
        if time() - max_wait > 1:
            break
        # print('not pass')
    

    # 이미지 url 추출
    index = 0; page = 1
    while True:
        # 페이지 넘어갔는지 체크
        while True:
            try:
                if 'true' == driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > div > div > a:nth-child({0})".format(str(page+1))).get_attribute('aria-current'):
                    break
            except selenium.common.exceptions.StaleElementReferenceException:
                continue
            # print(product_No, page, 'not pass')
        
        # 페이지 넘어갈 때 번호 초기화
        num = 1
        page_fault = False
        while True:
            # 리뷰 정보 추출
            while True:
                try:
                    info = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0})".format(str(num))).text
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    pass
                except:
                    page_fault = True; break
            if page_fault:
                page_fault = False; break
            
            
            info_list = list(info.split('\n'))

            # 리뷰 내용 추출
            while True:
                try:
                    content = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > div > div._1XNnRviOK8 > div > div._1YShY6EQ56 > div._19SE1Dnqkf".format(str(num))).text
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    pass
                except:
                    print('리뷰 내용',info_list)
                    print(product_No, index); return
            
            # 좋아요 수 추출
            while True:
                try:
                    like = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > div > div.fgI31XFKxN".format(str(num))).text
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    pass
                except:
                    print('좋아요 수',info_list)
                    print(product_No, index); return
            
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
                    while True:
                        try:
                            more = driver.find_element_by_css_selector("#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > a".format(str(num)))
                            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                            # ActionChains(driver).move_to_element(more).click(more).perform()
                            break
                        except selenium.common.exceptions.StaleElementReferenceException:
                            pass
                        except:
                            df.to_csv('/home/ubuntu/workspace/smartstore/lilydress/{}.csv'.format(product_No), encoding='utf-8-sig', mode='w')
                            print('더보기 클릭', info_list)
                            print(product_No, index); return
                        
                    while True:
                        try:
                            wait = driver.find_element_by_css_selector('#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > a'.format(str(num))).get_attribute('aria-expanded')
                        except selenium.common.exceptions.StaleElementReferenceException:
                            pass
                        except:
                            df.to_csv('/home/ubuntu/workspace/smartstore/lilydress/{}.csv'.format(product_No), encoding='utf-8-sig', mode='w')
                            print('이미지 더보기 대기',info_list)
                            print(product_No, index); return
                        if 'true' == wait:
                                break
                        else:
                            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                            # ActionChains(driver).move_to_element(more).click(more).perform()
                            print('이미지', product_No, index, num, wait)
                            print(info_list)
                            print(more.text)

                    # 이미지 url 저장
                    try:
                        img = WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > ul > li:nth-child({0}) > div > div > ul".format(str(num)))))
                    except Exception as ex:
                        df.to_csv('/home/ubuntu/workspace/smartstore/lilydress/{}.csv'.format(product_No), encoding='utf-8-sig', mode='w')
                        print('이미지 url 저장',info_list)
                        print(product_No, index, ex); return
                    html = img.get_attribute('outerHTML')
                    lst = list(html.split('"'))
                    img_url = list({x.split('?')[0] for x in lst if 'https' in x})
                # 클릭 되면서 이미지 미포함
                else:
                    img_url = ''

            # 데이터프레임에 추가
            df.loc[index] = [id, date, star, product_options, content, like, img_url]
            # print(index, id, )
            index += 1
            num += 1
            
        page += 1
        # 다음 버튼으로 페이지 넘기기
        next_page = WebDriverWait(driver, 10, poll_frequency=0.01).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div._2y6yIawL6t > div > div.cv6id6JEkg > div > div > a:nth-child({0})".format(str(page+1)))))
        if '다음' in next_page.text:
            page = 1
        elif next_page.text == '':
            break
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
        
    
    driver.close()

    print(product_No, 'runtime:', time() - start_time)
    
    df.to_csv('/home/ubuntu/workspace/smartstore/lilydress/{0}.csv'.format(product_No), encoding='utf-8-sig', mode='w')

if __name__ == '__main__':

    start = time()
    
    abc = parmap.map(crawl, url, pm_parallel=True, pm_processes=2)
    
    # for i in url:
    #     crawl(i)
    
    print('total runtime:', time() - start)
from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from math import ceil
import time
import re

def crawl(url, date):

    # 상품번호 추출
    product_No = url.split('products/')[-1]
    # print(product_No, 'start')
    # print(url)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(1)
    els = []

    # 리뷰 수 추출
    stack = 0
    while len(els) == 0:
        try:
            stack += 1
            els = driver.find_elements(by=By.PARTIAL_LINK_TEXT , value='리뷰')
        except Exception as ex:
            print(product_No, 'num:', len(els))
            print(ex)
            return
        if stack > 100: print(product_No, "리뷰 수 추출")

    for e in els:
        try:
            if e.text[-1].isdigit():
                element = e
                break
        except selenium.common.exceptions.StaleElementReferenceException:
            time.sleep(0.5)
            if any(chr.isdigit() for chr in e.text) and "(" not in e.text:
                element = e
                break
    
    try:
        count = ceil(int(element.text.split('뷰')[-1].replace(",",""))/20)
    except Exception as ex:
        print(product_No, 'count error')
        print(ex)
        for i in els:
            print(i.text, end='#')
            pass
        return

    # 리뷰 없으면 종료
    if count == 0:
        print(product_No, 'no review')
        return

    # 최신순 클릭
    while True:
        try:
            element = driver.find_element_by_link_text('최신순')
            break
        except Exception as ex:
            # print(product_No, "recent click error")
            # print(ex)
            pass
    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)

    # 페이지 넘기기
    page = 1
    while True:
        a = driver.find_element_by_class_name("review_list").text
        b = re.compile(r"\*\n\d{2}\.\d{2}\.\d{2}\.")
        c = b.findall(a)
        d = [i[2:] for i in c]

        date_max, date_min = d[0], d[-1]

        print(page)

        if date_min <= date <= date_max:
            break
        if date_max < date:
            if page % 10 == 1:
                page_element = driver.find_element_by_class_name('review_list').find_element_by_link_text('이전')
            else:
                page_element = driver.find_element_by_class_name('review_list').find_elements_by_link_text(str(page-1))[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
            page -= 1
        elif date_min > date:   
            try:
                page_element = driver.find_element_by_class_name('review_list').find_elements_by_link_text(str(page+1))[-1]
            except:
                page_element = driver.find_element_by_class_name('review_list').find_element_by_link_text('다음')
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
            page += 1


    time.sleep(10)

    driver.close()

if __name__ == "__main__":

    date = "20.08.02."

    start = time.time()

    crawl("https://smartstore.naver.com/lilydress/products/709465134", date)

    print("total run time:", time.time() - start)


    # https://smartstore.naver.com/i/v1/reviews/paged-reviews?page=1&pageSize=20&merchantNo=500119220&originProductNo=709465134&sortType=REVIEW_CREATE_DATE_DESC
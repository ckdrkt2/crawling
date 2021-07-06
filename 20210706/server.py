from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from multiprocessing import Pool
from math import ceil
import parmap
import tqdm
import time

url = pd.read_csv("/home/ubuntu/workspace/smartstore/lilydress/lilydress.csv")
url = list(url['0'])

def crawl(url):

    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    # 상품번호 추출
    product_No = url.split('products/')[-1]
    # print(product_No, 'start')
    # print(url)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome("/home/ubuntu/workspace/smartstore/chromedriver", options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(1)
    els = []
    ss = time.time()

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
        if stack > 100: print(product_No, "리뷰 수 추출"); print(driver.find_element(by=By.PARTIAL_LINK_TEXT , value='리뷰').text)

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

    # 리뷰 추출 부분
    index = 0
    for page in range(1, count+1):
        reviews = []
        
        # 페이지 넘기기
        compare = driver.find_element_by_id('REVIEW').text
        if page == 1: pass
        elif page % 10 == 1:
            page_element = driver.find_element_by_id('REVIEW').find_element_by_link_text('다음')
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
        else:
            page_element = driver.find_element_by_link_text('{0}'.format(str(page)))
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
        stack = 0
        if page != 1:
            while compare == driver.find_element_by_id('REVIEW').text:
                stack += 1
                if stack > 100:
                    print("turn page error:", product_No)
                pass
        
        # 리뷰 펼치기(사진)
        elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
        for element in elements:
            while True:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
                    print('stale error', product_No, page, index)
                except Exception as ex:
                    print(ex)
                    return

        # 리뷰 데이터 불러오기
        a = driver.find_element_by_id('REVIEW')
        b = a.text.split('최신순')[-1]
        c = list(b.split('\n'))
        d = list(a.get_attribute('outerHTML').split('최신순')[-1].split('"'))

        # 앞에 필요없는 데이터 제거
        while True:
            try:
                if '리뷰 더보기/접기' == c[0] or '평점' == c[0]:
                    break
                else:
                    c.pop(0)
            except Exception as ex:
                print('데이터제거', product_No)
                print(a.text); return
        
        # 리뷰 단위로 데이터 나누기
        i = 0
        while i < len(c)-1:
            lst = []
            if '리뷰 더보기/접기' == c[i] or '평점' == c[i]:
                lst.append(c[i])
                lst.append(c[i+1])
                i += 2
                
                while '리뷰 더보기/접기' != c[i] and '평점' != c[i]:
                    lst.append(c[i])
                    if i < len(c)-1:
                        # print(i)
                        i += 1
                    else:
                        break
                reviews.append(lst)

        # 나눈 데이터를 쪼개서 저장
        for n, review in enumerate(reviews):
            
            star, user_id, date, options, contents, like = '', '', '', '', '', ''
            p = None
            
            for i, value in enumerate(review):
                if value == '평점':
                    star = review[i+1]
                elif '**' in value:
                    user_id = value
                elif value == '신고' and p == None:
                    date = review[i-1]
                    p = i
                elif ': ' in value:
                    options = review[i]
                    p = i
                elif p != None:
                    try:
                        int(value)
                    except ValueError:
                        continue
                    like = value
                    
                    contents = '\n'.join(review[p+1:i])
                    break
            
            # HTML에서 해당 유저가 올린 사진 url 찾기
            img_id, img_url = None, []
            for m in d:
                if user_id in m:
                    img_id = user_id

                elif img_id != None and 'type=w640' in m:
                    img_url.append(m.split('?')[0])

                elif img_id != None and '****' in m and user_id not in m:
                    break
            if not len(img_url):
                img_url = ''
            else:
                img_url = list(set(img_url))

            df.loc[index] = [user_id, date, star, options, contents, like, img_url]

            index += 1

    print(product_No, "runtime:", int(time.time() - ss))

    df.to_csv('/home/ubuntu/workspace/smartstore/test/{0}.csv'.format(product_No), encoding='utf-8-sig', mode='w')

    driver.close()

if __name__ == "__main__":

    start = time.time()

    # while True:
    #     crawl("https://smartstore.naver.com/lilydress/products/343284038")

    aa = parmap.map(crawl, url, pm_parallel=True, pm_processes=2)

    print("total run time:", time.time() - start)
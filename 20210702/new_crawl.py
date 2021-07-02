from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from time import time, sleep
from multiprocessing import Pool
from math import ceil

df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

# url = pd.read_csv("/ss_urls.csv")
# url = list(url['0'])

url = 'https://smartstore.naver.com/lilydress/products/4152853436'

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('headless')

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
driver.implicitly_wait(1)

element = driver.find_elements(by=By.PARTIAL_LINK_TEXT , value='리뷰')[-1]
count = ceil(int(element.text.split('뷰')[-1])/20)

element = driver.find_element_by_link_text('최신순')
driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)

index = 0
for page in range(1, count+1):
    reviews = []

    # 페이지 넘기기
    if page == 1: pass
    elif page % 10 == 1:
        page_element = driver.find_element_by_id('REVIEW').find_element_by_link_text('다음')
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
    else:
        page_element = driver.find_element_by_link_text('{0}'.format(str(page)))
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
    
    sleep(1)

    # 리뷰 펼치기(사진)
    elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
    for element in elements:
        driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)

    sleep(1)

    # 리뷰 데이터 불러오기
    a = driver.find_element_by_id('REVIEW')
    b = a.text.split('최신순')[-1]
    c = list(b.split('\n'))
    d = list(a.get_attribute('outerHTML').split('최신순')[-1].split('"'))

    # 앞에 필요없는 데이터 제거
    while True:
        if '리뷰 더보기/접기' == c[0] or '평점' == c[0]:
            break
        else:
            c.pop(0)
    
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

df.to_csv('test.csv', encoding='utf-8-sig', mode='w')

driver.close()
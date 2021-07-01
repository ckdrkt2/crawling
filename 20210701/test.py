from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import time, sleep

df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', 'total'])

url = 'https://smartstore.naver.com/lilydress/products/554474687'

chrome_options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('window-size=1920x1080')
# options.add_argument("disable-gpu")

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(3)
driver.get(url)

element = driver.find_element_by_link_text('최신순')
driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)

sleep(1)

elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
# print(len(elements))
for element in elements:
    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
sleep(1)

a = driver.find_element_by_id('REVIEW')
b = a.text
c = list(b.split('\n'))
d = a.get_attribute('outerHTML')

while True:
    if '리뷰 더보기/접기' == c[0] or '평점' == c[0]:
        break
    else:
        c.pop(0)




reviews = []; index = 0
print('size:', len(c))
while index < len(c)-1:
    lst = []
    if '리뷰 더보기/접기' == c[index] or '평점' == c[index]:
        lst.append(c[index])
        lst.append(c[index+1])
        index += 2
        
        while '리뷰 더보기/접기' != c[index] and '평점' != c[index]:
            lst.append(c[index])
            if index < len(c)-1:
                # print(index)
                index += 1
            else:
                break
        reviews.append(lst)

# for i in reviews:
    # print(i)


for i, review in enumerate(reviews):

    star, user_id, date, options, contents, like = '', '', '', '', '', ''
    p = None

    for index, value in enumerate(review):
        if value == '평점':
            star = review[index+1]
        elif '**' in value:
            user_id = value
        elif value == '신고':
            p = index
            date = review[index-1]
            options = review[index+1]
        elif p != None:
            try:
                int(value)
            except ValueError:
                continue
            like = value
            print(review[p+2:index])
            contents = '\n'.join(review[p+2:index])

    df.loc[i] = [user_id, date, star, options, contents, like, review]
            
df.to_csv('test.csv', encoding='utf-8-sig', mode='w')

driver.close()
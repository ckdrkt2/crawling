from numpy import product
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep
from time import time

url = ['' for i in range(7)]
url[0] = ""
url[1] = ""
url[2] = ""
url[3] = ""
url[4] = ""
url[5] = ""
url[6] = ""

def crawl(url):

    start_time = time()

    driver = webdriver.Chrome()
    driver.implicitly_wait(3)
    driver.get(url)

    categori_css = "#content > div._2XqUxGzKDE > div._18UpKGc_hB > div > ul"
    
    # 리뷰 카테고리 클릭
    categoris = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_css_selector(categori_css)).text.split('\n')
    
    for index in range(len(list(categoris))):
        if '리뷰' in categoris[index]:
            element = driver.find_element_by_css_selector(categori_css + " > li:nth-child({})".format(str(index+1)))
            break
       
    ActionChains(driver).move_to_element(element).click(element).perform()
    sleep(1)

    # 최신순 클릭
    element = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_css_selector('#REVIEW > div > div.hmdMeuNPAt > div > div._1TvkeQbpJb > div._JEL2FoNN4 > ul > li:nth-child(2)'))
    ActionChains(driver).move_to_element(element).click(element).perform()
    sleep(1)

    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    # 이미지 url
    index = 0
    while True:
        num = 1

        while True:
            try:
                review = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num)))
            except:
                break
            
            info = review.text
            info_list = list(info.split('\n'))
            
            content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
            like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child(1) > div > div.KHHDezUtRz > div > div._3w28SVZeZM").text
            
            # 옵션 
            try:
                product_options = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div._3iYCagsFsO > div._301WLm00sr > div._31mfFx_-xd".format(str(num))).text
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
                    more = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                    
                    # 이미지 url 저장
                    img = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > ul".format(str(num)))
                    html = img.get_attribute('outerHTML')
                    lst = list(html.split('"'))
                    img_url = list({x.split('?')[0] for x in lst if 'https' in x})
                # 클릭 되면서 이미지 미포함
                else:
                    img_url = ''

            print(index, id)
            df.loc[index] = [id, date, star, product_options, content, like, img_url]

            index += 1
            num += 1
        
        
        next_page = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > div._1QyrsagqZm._2w8VqYht7m > a._3togxG55ie._2_kozYIF0B")
        # 다음 버튼이 보일 경우
        if '다음' in next_page.text:
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
            sleep(1)
        # 다음 버튼이 안 보일 경우
        else: break

    driver.close()

    print('runtime:', time() - start_time)

    return df

for i in range(0,len(url)):
    reviews = crawl(url[i])
    reviews.to_csv('output{}.csv'.format(i), encoding='utf-8-sig', mode='w')

from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep
from time import time

url = ['' for i in range(3)]
url[0] = ""
url[1] = ""
url[2] = ""

def crawl(url):

    start_time = time()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)

    name = driver.find_element_by_css_selector("#INTRODUCE > div > div._1Hbih69XFT > div:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > b").text

    categori_css = "#content > div._2XqUxGzKDE > div._18UpKGc_hB > div > ul"
    
    # 리뷰 카테고리 ?���?
    categoris = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_css_selector(categori_css)).text.split('\n')
    
    for index in range(len(list(categoris))):
        if '리뷰' in categoris[index]:
            element = driver.find_element_by_css_selector(categori_css + " > li:nth-child({})".format(str(index+1)))
            break
       
    ActionChains(driver).move_to_element(element).click(element).perform()

    # 최신?�� ?���?
    element = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_css_selector('#REVIEW > div > div.hmdMeuNPAt > div > div._1TvkeQbpJb > div._JEL2FoNN4 > ul > li:nth-child(2)'))
    ActionChains(driver).move_to_element(element).click(element).perform()

    df = pd.DataFrame(columns=['?��?��?��', '?��?��?��', '?��?��', '?��?��?��?��', '리뷰?��?��', '좋아?��', '?��미�??'])

    # ?��미�?? url
    index = 0
    while True:
        num = 1

        while True:
            try:
                info = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                info = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num))).text
            except:
                break
            
            info_list = list(info.split('\n'))

            try:
                content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
            try:
                like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div.KHHDezUtRz > div > div._3w28SVZeZM".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div.KHHDezUtRz > div > div._3w28SVZeZM".format(str(num))).text
            # ?��?�� 
            try:
                product_options = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div._3iYCagsFsO > div._301WLm00sr > div._31mfFx_-xd".format(str(num))).text
            except:
                product_options = ''
            
            # ?���? ?��?��
            if '?��?��' in info_list[0]:
                star  = info_list[1]
                id = info_list[2]
                date = info_list[3]
                img_url = ''
                print(index, id, info_list[0])
            # ?���? ?��?��
            else:
                star  = info_list[2]
                id = info_list[3]
                date = info_list[4]
                print(index, id, info_list[0])
                # ?���? ?��면서 ?��미�?? ?��?��
                if '?��미�?? ?��쳐보�?' in info_list:
                    # ?��보기 ?���?
                    more = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                    sleep(0.1)

                    # ?��미�?? url ????��
                    img = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > ul".format(str(num)))
                    html = img.get_attribute('outerHTML')
                    lst = list(html.split('"'))
                    img_url = list({x.split('?')[0] for x in lst if 'https' in x})
                # ?���? ?��면서 ?��미�?? 미포?��
                else:
                    img_url = ''

            # ?��?��?��?��?��?��?�� 추�??
            df.loc[index] = [id, date, star, product_options, content, like, img_url]

            index += 1
            num += 1
        
        
        next_page = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > div._1QyrsagqZm._2w8VqYht7m > a._3togxG55ie._2_kozYIF0B")
        # ?��?�� 버튼?�� 보일 경우
        if '?��?��' in next_page.text:
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
            sleep(1)
            # print("next page")
        # ?��?�� 버튼?�� ?�� 보일 경우
        else: break

    driver.close()

    print('runtime:', time() - start_time)

    df.to_csv('{}.csv'.format(name), encoding='utf-8-sig', mode='w')

for i in range(0,len(url)):
    crawl(url[i])
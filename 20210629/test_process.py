from multiprocessing import Process
from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from time import time

url = ['' for i in range(8)]
url[0] = "https://shopping.naver.com/style/style/stores/100103956/products/5622332194?NaPm=ct%3Dkq8pgmbi%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3Dde84db140a65fedc92f42ecc21bdba7f18105d21%7Ctrx%3D"
url[1] = "https://shopping.naver.com/style/style/stores/100144384/products/5624778400?NaPm=ct%3Dkq94by7p%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D441334267f0745041afc0aaa358848db30dbe3cb%7Ctrx%3D"
url[2] = "https://shopping.naver.com/style/style/stores/1000017495/products/4855024694?NaPm=ct%3Dkq97f06y%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D80c973e233542c9509497f5b8d777392a545865f%7Ctrx%3D"
url[3] = "https://shopping.naver.com/style/style/stores/1000007227/products/5647037895?NaPm=ct%3Dkqfuhfq7%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D8bc796e308dd5c6281b4efecd0793d0a812d5639%7Ctrx%3D"
url[4] = "https://shopping.naver.com/style/style/stores/100230577/products/5585392473?NaPm=ct%3Dkqfuihat%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D6f239477e5e62e4e8613cf171db32b41ed9459be%7Ctrx%3D"
url[5] = "https://shopping.naver.com/style/style/stores/1000016941/products/5615618786?NaPm=ct%3Dkqfzi2mx%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D4c7d1e6b1026093384886723d1d49b4b492aced7%7Ctrx%3D"
url[6] = "https://shopping.naver.com/style/style/stores/1000020042/products/5637202841?NaPm=ct%3Dkqfzikwm%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D4a0c05e77379043a3e58c8aa9c0642af737e9f1d%7Ctrx%3D"
url[7] = "https://shopping.naver.com/style/style/stores/100290446/products/5639723770?NaPm=ct%3Dkqfzjc6f%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3Dee0227e745ef38433028ef218b5d83e8f3617972%7Ctrx%3D"
# url[5] = "https://shopping.naver.com/style/style/stores/100011460/products/4930897325?NaPm=ct%3Dkqafq13x%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D00e7f021e45a4f32600c3b50ff2a48bcd35f8840%7Ctrx%3D"
# url[6] = "https://shopping.naver.com/style/style/stores/1000007227/products/5315814234?NaPm=ct%3Dkqajdh7y%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3D3d07b2ac9c5cb71ac17c55a11606a4f10cc4b348%7Ctrx%3D"
# url[7] = "https://shopping.naver.com/style/style/stores/1000018214/products/3729385447?NaPm=ct%3Dkqamutl1%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3Da58861ab65a8ca56c3f0ee3ddf1b9d15930c34b7%7Ctrx%3D"
# url[8] = "https://shopping.naver.com/style/style/stores/1000008005/products/4448262736?NaPm=ct%3Dkqamh5tq%7Cci%3Dshoppingwindow%7Ctr%3Dswl%7Chk%3Da5b888f413ab7f2a8559a535d895cc31a2cfc92a%7Ctrx%3D"

def crawl(url):

    start_time = time()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)

    name = driver.find_element_by_css_selector("#INTRODUCE > div > div._1Hbih69XFT > div:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > b").text

    categori_css = "#content > div._2XqUxGzKDE > div._18UpKGc_hB > div > ul"
    
    # 리뷰 카테고리 클릭
    categoris = WebDriverWait(driver, 10, poll_frequency=0.1).until(lambda x:x.find_element_by_css_selector(categori_css)).text.split('\n')
    
    for index in range(len(list(categoris))):
        if '리뷰' in categoris[index]:
            element = driver.find_element_by_css_selector(categori_css + " > li:nth-child({})".format(str(index+1)))
            break
       
    ActionChains(driver).move_to_element(element).click(element).perform()

    # 최신순 클릭
    element = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#REVIEW > div > div.hmdMeuNPAt > div > div._1TvkeQbpJb > div._JEL2FoNN4 > ul > li:nth-child(2)')))
    # driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
    ActionChains(driver).move_to_element(element).click(element).perform()
    sleep(0.5)

    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    # 이미지 url
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
                # print(index, id, info_list[0])
            # 사진 있음
            else:
                star  = info_list[2]
                id = info_list[3]
                date = info_list[4]
                # print(index, id, info_list[0])
                # 클릭 되면서 이미지 포함
                if '이미지 펼쳐보기' in info_list:
                    # 더보기 클릭
                    # more = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))
                    more = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))))
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                    sleep(0.1)

                    # 이미지 url 저장
                    img = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > ul".format(str(num)))
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
        
        
        next_page = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div.hmdMeuNPAt > div > div._1QyrsagqZm._2w8VqYht7m > a._3togxG55ie._2_kozYIF0B")))
        # 다음 버튼이 보일 경우
        if '다음' in next_page.text:
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
            sleep(1)
            # print("next page")
        # 다음 버튼이 안 보일 경우
        else: break

    driver.close()

    print(name, 'runtime:', time() - start_time)

    df.to_csv('{}.csv'.format(name), encoding='utf-8-sig', mode='w')

if __name__ == '__main__':

    procs = []

    start = time()

    urls = []
    for j in range(3):
        for i in url:
            urls.append(i)

    for i, num in enumerate(urls):
        proc = Process(target=crawl, args=(num,))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print('total runtime:', time() - start)
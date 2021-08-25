from bs4 import BeautifulSoup
from selenium import webdriver
import time

class crawl():

    def __init__(self, url):
        self.__url = url

    def getinfo_se(self):
        
        title = ""
        productNo = self.__url.split('/')[-1]
        img = ""
        reviews = "0"

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.__url)

        # 사이트 내 데이터가 있는 tag 저장
        container = BeautifulSoup(driver.find_element_by_id("container").get_attribute('outerHTML'), 'html.parser')
        while container == None: pass
        driver.close()


        # 상품명 추출
        title = container.find("h1").text

        # 이미지 src url 추출
        image_div = container.findAll("div", "swiper-slide-active")[0]
        img = image_div['data-thumb']

        
        # 리뷰수 추출
        a_tags = container.findAll("span", "counting")[0]
        reviews = a_tags.text[1:-1]

        return {'상품명':title, '상품번호':productNo, '이미지':img, '리뷰수':reviews}


if __name__ == "__main__":

    url = "https://www.brandi.co.kr/products/45396033"

    info = crawl(url)

    s = time.time()

    print(info.getinfo_se())

    print(time.time()-s)
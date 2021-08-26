from bs4 import BeautifulSoup
from selenium import webdriver
from request import requests
import time

class crawl():

    def __init__(self, url):
        self.__url = url
        self.__header = {'Authorization':'3b17176f2eb5fdffb9bafdcc3e4bc192b013813caddccd0aad20c23ed272f076_1423639497'}

    def getinfo(self):

        title = ""
        productNo = self.__url.split('/')[-1]
        img = ""
        reviews = 0
        
        # 해당 상품의 정보를 API에서 json 형태로 추출
        response = requests.get("https://cf-api-c.brandi.me/v1/web/products/{0}?res-type=section0&version=2102".format(productNo), headers=self.__header)
        
        data = response.json()['data']

        # 상품명 추출
        title = data['name']

        # 이미지 src url 추출
        img = data['image_thumbnail_url']

        # 리뷰수 추출
        # 브랜디 자체에서도 리뷰수를 따로 저장해두지 않고 텍스트 리뷰와 포토 리뷰를 카운트한 값을 출력
        offset = 0
        while True:
            response = requests.get("https://cf-api-v2.brandi.me/v2/web/products/{0}/reviews?version=2101&limit=100&offset={1}&tab-type=all".format(productNo, offset), headers=self.__header)
            review = len(response.json()['data'])
            if review > 0: reviews += review
            else: break
            offset += 100

        return {'상품명':title, '상품번호':productNo, '이미지':img, '리뷰수':reviews}

if __name__ == "__main__":

    url = "https://www.brandi.co.kr/products/38042677"

    info = crawl(url)

    print(info.getinfo())
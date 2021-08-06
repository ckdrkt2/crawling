import requests
from bs4 import BeautifulSoup

class crawl():

    def __init__(self, url):
        self.__url = url

    def getinfo(self):
        
        title = ""
        productNo = self.__url.split('/')[-1]
        img = ""
        reviews = "0"

        response = requests.get(self.__url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 사이트 내 데이터가 있는 tag 저장
        content = soup.find("div", id="content")

        # 상품명 추출
        title = content.find("div", id="_share")['data-title']

        # 이미지 src url 추출
        images = content.find_all("img")
        for image in images:
            if "대표이미지" in image['alt']:
                img = image['src']
                break

        # 리뷰수 추출
        a_tags = content.find_all("a")
        for a_tag in a_tags:
            if "#REVIEW" in a_tag['href']:
                reviews = a_tag.text
                break

        return {'상품명':title, '상품번호':productNo, '이미지':img, '리뷰수':reviews}


if __name__ == "__main__":

    url = ""

    info = crawl(url)

    print(info.getinfo())
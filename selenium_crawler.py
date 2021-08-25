from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from request import requests
import re

import pandas as pd

'''
webdriver 속도가 너무 느려서 동적인 부분을 제외하고 requests와 BeautifulSoup를 사용해서 데이터 수집
webdriver의 find_element가 너무 많은 오류를 만들어서 이 부분도 최대한 BeautifulSoup로 대체
7400개 리뷰 기준 1747s -> 682s

데이터 추출 부분은 전반적으로 class 이름을 사용하지 않고 특정 tag나 특정 link_text를 이용해서 추출
ex) em tag는 리뷰 별점을 위해서만 존재 / 판매자 텍스트는 판매자 댓글로 유일

동영상 링크의 경우에는
서버 내에 동영상 원본 소스가 있고 그 링크를 통해서 원본 동영상을 확인가능
스마트스토어의 경우에는 원본 소스 링크를 사용하지 않고 실시간 스트리밍 방식을 사용(.m3u8)
따라서 selenium이나 requests를 사용하면 원본 소스 링크가 아니라 m3u8 파일만 확인이 가능하고
이를 동영상으로 변환을 해야 리뷰 동영상을 추출 가능
'''

def crawl(url, date):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(1)

    # 상품번호 추출
    product_No = url.split('products/')[-1]

    # 리뷰 수 추출
    reviews = "0"
    html = BeautifulSoup(requests.get(url).text, 'html.parser')
    a_tags = html.findAll("a")
    for a_tag in a_tags:
        if "#REVIEW" in a_tag['href']:
            reviews = a_tag.text
            break
    reviews = int(reviews.replace(",",""))
    # 리뷰 없으면 종료
    if not reviews:
        print(product_No, 'no review')
        return

    # 최신순 클릭
    while True:
        try:
            element = driver.find_element_by_class_name('review_list').find_element_by_link_text('최신순')
            break
        except Exception as ex:
            pass
    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
    
    # 기준 날짜 설정
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%y.%m.%d.')
    today = datetime.now().strftime('%y.%m.%d.')


    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '판매자댓글', '이미지'])

    # 리뷰 추출 부분
    count = (reviews-1) // 20 + 1
    index, page = 0, 1
    loop_break = False; last_date = today
    while page < count+1:

        print("page:", page, " date:", last_date)

        REVIEW = driver.find_element_by_id('REVIEW')

        # 현재 페이지와 page 변수가 같은지 확인
        page_element = REVIEW.find_element_by_link_text('{0}'.format(str(page)))
        while page_element.get_attribute('aria_current') == 'false': pass       # 페이지와 page 변수가 같아질 때까지 대기
    
        # 리뷰 펼치기(사진)
        i = 0
        while True:
            try:
                element = REVIEW.find_elements_by_link_text('리뷰 더보기/접기')[i]
                driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
                i += 1
            except:
                break

        # 리뷰 리스트 부분 추출
        review_list = BeautifulSoup(driver.find_element_by_class_name('review_list').get_attribute('outerHTML'), 'html.parser')
        
        page += 1
        # 페이지 넘기기
        if page < count+1:
            if page % 10 == 1:
                page_element = REVIEW.find_element_by_link_text('다음')
                driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
            else:
                page_element = REVIEW.find_element_by_link_text('{0}'.format(str(page)))
                driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)


        # 필요한 부분 추출(ul/li 태그 이용)
        ul_tag = ""
        ul_tags = review_list.findAll('ul')
        for i in ul_tags:
            if '신고' in i.text:
                ul_tag = i
                break
        if ul_tag == "": return

        li_tags = ul_tag.findAll("li")
        li_tag_list = []
        for i in li_tags:
            if '프로필_image' in str(i):
                li_tag_list.append(i)

        # 날짜 계산
        max_date = re.compile(r"\d{2}\.\d{2}\.\d{2}\.").findall(li_tag_list[0].text)[0]
        min_date = re.compile(r"\d{2}\.\d{2}\.\d{2}\.").findall(li_tag_list[-1].text)[0]
        
        if min_date == today or min_date > last_date:   # 현재 페이지의 가장 작은 날짜가 오늘 -> 페이지 전체가 오늘 날짜이므로 패스
            continue                                    # 현재 페이지의 가장 작은 날짜가 마지막 추출 데이터의 날짜보다 큼 -> 리뷰가 추가되었으므로 해당 날짜까지 패스
        if max_date  < date:                            # 현재 페이지의 가장 큰 날짜가 기준 날짜보다 작음 -> 범위 초과이므로 break
            break

        # 추출한 li_tag 검사
        for li_tag in li_tag_list:

            review_date = re.compile(r"\d{2}\.\d{2}\.\d{2}\.").findall(li_tag.text)[0]

            if review_date == today:    # 추출한 데이터의 날짜가 오늘이면 패스
                continue                
            if review_date < date:      # 추출한 데이터의 날짜가 범위 밖이면
                loop_break = True       # break 비트 True -> while loop 마지막에 break
                break
            
            last_date = review_date     # 마지막으로 추출한 데이터의 날짜를 last_date 변수에 저장

            # 리뷰 평가 점수 추출
            try:
                star = li_tag.find('em').text
            except:
                print(li_tag);return

            # 리뷰 좋아요 수 / 상품옵션 추출
            button_tags = li_tag.findAll("button")
            if len(button_tags) > 1:
                options = button_tags[0].text
                like = button_tags[1].text
            else:
                options = ""
                like = button_tags[0].text

            # 리뷰 작성자 아이디 추출
            user_id = li_tag.find("strong").text

            # 리뷰 내용 추출 / 정확도를 위해 부득이하게 class명 사용
            contents = li_tag.find("div", "YEtwtZFLDz").text
            
            # 판매자 댓글 추출
            comments = None
            strong_tags = li_tag.findAll("strong")
            for strong_tag in strong_tags:
                if "판매자" == strong_tag.text:
                    comments = strong_tag.findParent("div").findParent("div").findParent("div").find("p").text
                    break

            # 이미지 url 추출
            img_list = []
            attaches = li_tag.findAll('ul')
            if attaches:
                attach = attaches[0]
                img_tags = attach.findAll("img")
                for img_tag in img_tags:
                    src = img_tag['src'].split('?')[0]
                    if 'data' not in src: img_list.append(src)
                img_url = ' | '.join(img_list)
            else: img_url = ""

            df.loc[index] = [user_id, review_date, star, options, contents, like, comments, img_url]

            index += 1

        if loop_break: break
        

    df.to_csv('test/{0}.csv'.format(product_No), encoding='utf-8-sig', mode='w')

    driver.close()

if __name__ == "__main__":
    
    date = "2021-07-25"

    url = "https://smartstore.naver.com/lilydress/products/709465134"

    crawl(url, date)
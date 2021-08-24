from selenium import webdriver
import pandas as pd
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup


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
    while True:
        try:
            a_tags = driver.find_element_by_id("content").find_elements_by_tag_name("a")
            break
        except: pass
        
    for a_tag in a_tags:
        if "#REVIEW" in a_tag.get_attribute("href"):
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

        # print(page)

        REVIEW = driver.find_element_by_id('REVIEW')

        page_element = REVIEW.find_element_by_link_text('{0}'.format(str(page)))
        while page_element.get_attribute('aria_current') == 'false': pass
    
        # 리뷰 펼치기(사진)
        i = 0
        while True:
            try:
                element = REVIEW.find_elements_by_link_text('리뷰 더보기/접기')[i]
                driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
                i += 1
            except:
                break

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
        
        if min_date == today or min_date > last_date:
            continue
        if max_date  < date:
            break

        for li_tag in li_tag_list:

            review_date = re.compile(r"\d{2}\.\d{2}\.\d{2}\.").findall(li_tag.text)[0]

            if review_date == today:
                continue
            if review_date < date:
                loop_break = True
                break
            
            last_date = review_date

            try:
                star = li_tag.find('em').text
            except:
                print(li_tag);return

            button_tags = li_tag.findAll("button")
            if len(button_tags) > 1:
                options = button_tags[0].text
                like = button_tags[1].text
            else:
                options = ""
                like = button_tags[0].text

            user_id = li_tag.find("strong").text

            contents = li_tag.find("div", "YEtwtZFLDz").text

            img_list = []

            comments = None
            p_tags = li_tag.findAll("p")    # 좀 더 돌려보기
            for p_tag in p_tags:
                if p_tag.find("strong") == None:
                    print(p_tag)
                    comments = p_tag.text
                    break

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

    start = time.time()
    
    date = "2020-10-20"

    # url = "https://smartstore.naver.com/lilydress/products/3895706314"
    url = "https://smartstore.naver.com/lilydress/products/709465134"
    # url = "https://smartstore.naver.com/rankingdak/products/521363595"

    crawl(url, date)

    print("total run time:", time.time() - start)
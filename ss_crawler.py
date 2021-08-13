from selenium import webdriver
import selenium
import pandas as pd
import time
import re
from tqdm import tqdm

def crawl(url):

    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    # 상품번호 추출
    product_No = url.split('products/')[-1]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(1)

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
            # print(product_No, "recent click error")
            # print(ex)
            pass
    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
    
    # 리뷰 추출 부분
    count = reviews // 20 + 1
    index = 0
    for page in tqdm(range(1, count+1)):
        
        # 페이지 넘기기
        compare = driver.find_element_by_id('REVIEW').text
        if page == 1: pass
        elif page % 10 == 1:
            page_element = driver.find_element_by_id('REVIEW').find_element_by_link_text('다음')
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
        else:
            page_element = driver.find_element_by_link_text('{0}'.format(str(page)))
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", page_element)
        stack = 0
        if page != 1:
            while compare == driver.find_element_by_id('REVIEW').text:
                stack += 1
                if stack > 100:
                    print("turn page error:", product_No)
                pass
        
        # 리뷰 펼치기(사진)
        elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
        for element in elements:
            while True:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
                    break
                except selenium.common.exceptions.StaleElementReferenceException:
                    elements = driver.find_elements_by_link_text('리뷰 더보기/접기')
                    print('stale error', product_No, page, index)
                except Exception as ex:
                    print(ex)
                    return

        ul_tags = driver.find_element_by_class_name('review_list').find_elements_by_tag_name('ul')
        ul_tag = ""
        for i in ul_tags:
            if '신고' in i.text:
                ul_tag = i
                break
        if ul_tag == "": return 

        # 필요한 li tag 추출
        li_tags = ul_tag.find_elements_by_tag_name("li")
        li_tag_list = []
        for i in li_tags:
            if '신고' in i.text:
                li_tag_list.append(i)

        for li_tag in li_tag_list:

            star = li_tag.find_element_by_tag_name("em").text

            button_tags = li_tag.find_elements_by_tag_name("button")
            if len(button_tags) > 1:
                options = button_tags[0].text
                like = button_tags[1].text
            else:
                options = ""
                like = button_tags[0].text

            user_id = li_tag.find_element_by_tag_name("strong").text

            try:
                date = re.compile(r"\d{2}\.\d{2}\.\d{2}\.").findall(li_tag.text)[0]
            except:
                print(page)
                print(li_tag.text)
                return

            contents = li_tag.find_element_by_class_name("YEtwtZFLDz").text

            img_list = []

            attaches = li_tag.find_elements_by_tag_name('ul')
            if attaches:
                attach = attaches[0]
                img_tags = attach.find_elements_by_tag_name("img")
                for img_tag in img_tags:
                    src = img_tag.get_attribute('src').split('?')[0]
                    if 'data' not in src: img_list.append(src)
                img_url = ' | '.join(img_list)
            else: img_url = ""

            df.loc[index] = [user_id, date, star, options, contents, like, img_url]

            index += 1

    df.to_csv('test/{0}.csv'.format(product_No), encoding='utf-8-sig', mode='w')

    driver.close()

if __name__ == "__main__":

    start = time.time()
    
    crawl("https://smartstore.naver.com/lilydress/products/690142213")

    print("total run time:", time.time() - start)
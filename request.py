import requests
import pandas as pd
from datetime import datetime

def crawl(url, date):

    url_elements = url.split('/')

    productNo = url_elements[-1]

    response = requests.get(url, stream=True)

    merchantNo = ""; ex = ""; script_bit = False; id_bit = False
    for chunk in response.iter_content(chunk_size=512):
        current = ex + chunk.decode('utf-8', errors="ignore")
        if "window.__PRELOADED_STATE__" in current:
            script_bit = True
        if script_bit and 'payReferenceKey' in current:
            idx = current.find('payReferenceKey')
            merchantNo = current[idx+18:idx+27]
        if script_bit and '"id":"{}"'.format(productNo) in current:
            id_bit = True
        if id_bit and '"productNo":' in current:
            idx = current.find('"productNo":')
            productNo = current[idx+13:idx+23].replace('"','')
            break
        ex = current[-30:]
    
    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page=1&pageSize=20&merchantNo={0}&originProductNo={1}&sortType=REVIEW_CREATE_DATE_DESC'.format(merchantNo, productNo)
    response = requests.get(requests_url)
    
    # 리뷰가 없는 경우 패스
    if response.text == 'OK':
        return

    json = response.json()

    total_page = json['totalPages']
    total_reviews = json['totalElements']

    # 페이지 체크
    while True:
        try:
            requests_url = requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(total_page, merchantNo, productNo)
            response = requests.get(requests_url)
            json = response.json()
            break
        except:
            print(requests_url)
            print(response.text)

    # 전체 데이터가 기준일 안에 포함될 경우
    if json['contents'][-1]['createDate'][:10] < date:

        # 페이지 찾기
        bot, top = 1, total_page

        while True:
            current_page = (bot + top) // 2

            requests_url = requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(current_page, merchantNo, productNo)
            response = requests.get(requests_url)
            json = response.json()

            highest_date = json['contents'][0]['createDate'][:10] 
            lowest_date = json['contents'][-1]['createDate'][:10]

            # print(current_page, lowest_date, date, highest_date)

            if lowest_date <= date <= highest_date:
                break
            elif date > highest_date:
                top = current_page
            elif date < lowest_date:
                bot = current_page

    # 전체 데이터 중에 기준일이 포함되는 경우
    else:
        current_page = total_page

    index = 0
    df = pd.DataFrame(columns=['리뷰ID', '작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    today = datetime.now().strftime('%Y-%m-%d')
    page = current_page
    addreview = False
    while page > 0:

        print("running page:", current_page - page + 1, "/", current_page)

        requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(page, merchantNo, productNo)

        json = requests.get(requests_url).json()
        if json['totalElements'] > total_reviews:
            page += ((json['totalElements'] - total_reviews - 1) // 20) + 1
            total_reviews = json['totalElements']
            addreview = True
            continue

        reviews = json['contents']
        for i in range(len(reviews)-1, -1, -1):

            createDate = reviews[i]['createDate'][:10]
            if today == createDate:
                page = 0
                break
            if date >= createDate:
                continue

            user_id = reviews[i]['writerMemberId']

            star = reviews[i]['reviewScore']

            try:
                options = reviews[i]['productOptionContent']
            except:
                options = ""

            contents = reviews[i]['reviewContent']

            try:
                like = reviews[i]['helpCount']
            except: like = 0

            img_url = []
            if reviews[i]['reviewAttaches']:
                for attach in reviews[i]['reviewAttaches']:
                    img_url.append(attach['attachUrl'])
            if not img_url: img_url = ""

            df.loc[index] = [reviews[i]['id'], user_id, createDate, star, options, contents, like, img_url]
            

            index += 1
        page -= 1

    df.to_csv('request/{0}.csv'.format(url_elements[-1]), encoding='utf-8-sig', mode='w')

    return addreview

if __name__ == "__main__":

    # url = "https://smartstore.naver.com/ssg01/products/4608892138"
    # url = "https://smartstore.naver.com/lilydress/products/709465134"
    # url = "https://smartstore.naver.com/ks1st/products/4497145782"
    url = "https://smartstore.naver.com/rankingdak/products/521363595"
    
    date = '2021-07-20'

    # url = pd.read_csv("moo.csv")
    # url = list(url['0'])
    # for i in url:
    #     crawl(i, date)

    crawl(url, date)
import requests
import pandas as pd
from datetime import datetime, timedelta


def get_response(page,merchantNo, productNo):
    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(page, merchantNo, productNo)
    return requests.get(requests_url)

def crawl(url, date):

    url_elements = url.split('/')
    # 상품번호
    productNo = url_elements[-1]

    # 판매자 번호 & origin상품번호 추출
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
    

    # 페이지 수와 리뷰수 추출
    response = get_response(1, merchantNo, productNo)
    # 리뷰가 없는 경우 패스
    if response.text == 'OK':
        return False

    json = response.json()
    # 범위에 해당하는 데이터가 없을 경우 패스
    if json['contents'][0]['createDate'][:10] < date:
        return False

    total_page = json['totalPages']
    total_reviews = json['totalElements']


    # 페이지 체크
    while True:
        try:
            response = get_response(total_page, merchantNo, productNo)
            json = response.json()
            break
        except: # 총 페이지와 실제 페이지 사이에 차이가 있을 경우 차이를 감소
            print("delay error", url)
            total_page -= 1

    # 날짜 조정
    date = datetime.strptime(date, '%Y-%m-%d')
    day = timedelta(1)
    date = str(date-day)[:10]

    # 전체 데이터가 기준일 안에 포함될 경우
    if json['contents'][-1]['createDate'][:10] < date:

        # 시작해야할 페이지 찾기
        bot, top = 1, total_page
        
        while True:
            date_page = (bot + top) // 2
            
            response = get_response(date_page, merchantNo, productNo)
            json = response.json()

            highest_date = json['contents'][0]['createDate'][:10] 
            lowest_date = json['contents'][-1]['createDate'][:10]
            
            if lowest_date <= date <= highest_date or bot == date_page:
                break
            elif date > highest_date:
                top = date_page
            elif date < lowest_date:
                bot = date_page            

    # 전체 데이터가 기준일에 포함되는 경우
    else:
        date_page = total_page   # 전체 데이터 추출


    # 리뷰 추출
    index = 0
    df = pd.DataFrame(columns=['리뷰ID', '작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지', '비디오'])
    today = datetime.now().strftime('%Y-%m-%d')
    page = date_page
    while page > 0:

        # 현재 페이지 확인
        print("running page:", date_page - page + 1, "/", date_page)

        json = get_response(page, merchantNo, productNo).json()
        
        if json['totalElements'] > total_reviews:
            if page < json['totalPages']:
                page += ((json['totalElements'] - total_reviews - 1) // 20) + 1
            total_reviews = json['totalElements']
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
            print(type(star))

            try:
                options = reviews[i]['productOptionContent']
            except: options = ""

            contents = reviews[i]['reviewContent']

            try:
                like = reviews[i]['helpCount']
            except: like = 0

            img_list = []
            if reviews[i]['reviewAttaches']:
                for attach in reviews[i]['reviewAttaches']:
                    img_list.append(attach['attachUrl'])
            img_url = " | ".join(img_list)

            if reviews[i]['reviewAttaches']:
                for attach in reviews[i]['reviewAttaches']:
                    

            # dataframe에 저장
            df.loc[index] = [reviews[i]['id'], user_id, createDate, star, options, contents, like, img_url, video_url]
            
            index += 1
        page -= 1

    df.to_csv('request/{0}.csv'.format(url_elements[-1]), encoding='utf-8-sig', mode='w')

    return True

if __name__ == "__main__":

    date = '2020-08-09'

    url = "https://smartstore.naver.com/lilydress/products/709465134"

    crawl(url, date)
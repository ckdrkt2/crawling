import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def get_response(page,merchantNo, productNo):
    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(page, merchantNo, productNo)
    return requests.get(requests_url)

def get_inkey(vid):
    requests_url = 'https://smartstore.naver.com/i/v1/reviews/video/inkey/{0}'.format(vid)
    return requests.get(requests_url).json()['inKey']

def get_video_url(vid, inKey):
    requests_url = 'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{0}?key={1}'.format(vid, inKey)
    return requests.get(requests_url).json()['videos']['list'][0]['source']

def get_compare_id(merchantNo, productNo):
    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page=1&pageSize=20&merchantNo={0}&originProductNo={1}&sortType=REVIEW_CREATE_DATE_DESC'.format(merchantNo, productNo)
    return requests.get(requests_url).json()['contents'][0]['id']
    

def crawl(url, date):

    if date == 'all': date = '2000-01-01'

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
    else: date_page = total_page   # 전체 데이터 추출
    
    # 페이지 저장
    point_page = date_page
    point_id = get_response(point_page, merchantNo, productNo).json()['contents'][0]['id']

    # 리뷰 추출
    index = 0
    df = pd.DataFrame(columns=['리뷰ID', '작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지', '비디오'])
    today = datetime.now().strftime('%Y-%m-%d')
    createDate = None
    page = date_page
    while page > 0:        

        # 현재 페이지 확인
        # print("running page:", date_page - page + 1, "/", date_page)
        # print("running page:", page)

        json = get_response(page, merchantNo, productNo).json()

        reviews = json['contents']
        
        for i in range(len(reviews)-1, -1, -1):

            createDate = reviews[i]['createDate']
            if today == createDate[:10]:
                page = 0
                break
            if date >= createDate[:10]:
                continue

            user_id = reviews[i]['writerMemberId']

            star = reviews[i]['reviewScore']

            try:
                options = reviews[i]['productOptionContent']
            except: options = ""

            contents = reviews[i]['reviewContent']

            try:
                like = reviews[i]['helpCount']
            except: like = 0

            img_list = []
            video_list = []
            if reviews[i]['reviewAttaches']:
                for attach in reviews[i]['reviewAttaches']:
                    img_list.append(attach['attachUrl'])
                    
                    # video url 추출
                    if 'attachVid' in attach:
                        vid = attach['attachVid']
                        inkey = get_inkey(vid)
                        video_list.append(get_video_url(vid, inkey))
            
            img_url = " | ".join(img_list)
            video_url = " | ".join(video_list)

            review_comment = []
            if 'reviewComments' in reviews[i]:
                for comment in reviews[i]['reviewComments']:
                    review_comment.append(comment['commentContent'])

            review_id = reviews[i]['id']

            # dataframe에 저장
            df.loc[index] = [review_id, user_id, createDate, star, options, contents, like, img_url, video_url]
            
            index += 1

        if (point_page - page) == 100:
            compare_id = get_response(point_page, merchantNo, productNo).json()['contents'][0]['id']
            print(page, "검사")
            if point_id == compare_id:
                point_page = page
                point_id = review_id
            else:
                print("review added", "index:", index)
                while True:
                    reviews = get_response(point_page, merchantNo, productNo).json()['contents']
                    review_id_list = [review['id'] for review in reviews]
                    if point_id in review_id_list:
                        page = point_page + 1
                        point_id = reviews[0]['id']
                        break
                    else:
                        point_page += 1
                print(page)

        page -= 1

    df.to_csv('{0}.csv'.format(url_elements[-1]), encoding='utf-8-sig', mode='w')

    return True

if __name__ == "__main__":

    date = '2021-07-18'

    url = "https://smartstore.naver.com/rankingdak/products/521363595"

    while True:
        crawl(url, date)
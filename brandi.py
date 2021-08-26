import requests
import pandas as pd
from datetime import datetime

def get_data(productNo, offset):

    headers = {'Authorization': '3b17176f2eb5fdffb9bafdcc3e4bc192b013813caddccd0aad20c23ed272f076_1423639497'}
    request_url = "https://cf-api-v2.brandi.me/v2/web/products/{0}/reviews?version=2101&limit=100&offset={1}&tab-type=all".format(productNo, offset)
    response = requests.get(request_url, headers=headers)
    return response.json()['data']

def crawl(url, date):
    
    productNo = url.split('/')[-1]

    # 리뷰가 없을경우 종료
    reviews = get_data(productNo, 0)
    count = len(reviews)
    if not count: return
    
    df = pd.DataFrame(columns=['리뷰ID', '작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])
    date = datetime.strptime(date, '%Y-%m-%d')
    loop_break = False
    index, offset = 0, 0
    while count:

        for review in reviews:

            createDate = datetime.fromtimestamp(int(review['created_time']))

            if createDate < date:
                loop_break = True
                break

            review_id = review['id']

            user_id = review['user']['name']

            star = review['evaluation']['satisfaction']

            options = review['product']['option_name']

            contents = review['text']

            like = review['like_count']

            if 'images' in review:
                img_list = []
                for i in review['images']:
                    img_list.append(i['image_url'])
                img_url = ' | '.join(img_list)
            else:
                img_url = ""

            df.loc[index] = [review_id, user_id, createDate, star, options, contents, like, img_url]
            index += 1

        if loop_break: break

        offset += 100
        reviews = get_data(productNo, offset)
        count = len(reviews)
    
    df.to_csv('{0}.csv'.format(productNo), encoding='utf-8-sig', mode='w')

        
if __name__ == "__main__":

    date = '2021-07-09'

    url = "https://www.brandi.co.kr/products/34760766"

    crawl(url, date)

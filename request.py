import requests
import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import json

# url = "https://smartstore.naver.com/lilydress/products/709465134"
url = "https://smartstore.naver.com/ks1st/products/4497145782"
date = '2021-08-03'

merchantNo = {'lilydress':500119220, 'ks1st':510072297}

url_elements = url.split('/')

productNo, merchant = url_elements[-1], url_elements[-3]

# requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page=1&pageSize=20&merchantNo={0}&originProductNo={1}&sortType=REVIEW_CREATE_DATE_DESC'.format(merchantNo[merchant], productNo)

# payload = {'key1': 'value1', 'key2': 'value2'}
# response = requests.get('https://smartstore.naver.com/ks1st/products/4497145782', params=payload)

# a = response.text
# b = BeautifulSoup(response.text, 'html.parser').findAll('script')



exit()
json = response.json()

total_page = json['totalPages']

index = 0
df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

for page in tqdm(range(1, total_page+1)):

    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(page, merchantNo[merchant], productNo)

    json = requests.get(requests_url).json()

    for review in json['contents']:

        user_id = review['writerMemberId']

        date = review['createDate']

        star = review['reviewScore']

        try:
            options = review['productOptionContent']
        except:
            options = ""

        contents = review['reviewContent']

        try:
            like = review['helpCount']
        except: like = 0

        img_url = []
        if review['reviewAttaches']:
            for attach in review['reviewAttaches']:
                img_url.append(attach['attachUrl'])
        if not img_url: img_url = ""

        df.loc[index] = [user_id, date, star, options, contents, like, img_url]
        
        index += 1

df.to_csv('request/{0}.csv'.format(productNo), encoding='utf-8-sig', mode='w')
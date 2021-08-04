import requests
import pandas as pd
import time
from tqdm import tqdm

# url = "https://smartstore.naver.com/lilydress/products/709465134"
# url = "https://smartstore.naver.com/lilydress/products/341516198"
# url = "https://smartstore.naver.com/ks1st/products/4497145782"
# url = "https://smartstore.naver.com/ks1st/products/4497224588"
# url = "https://smartstore.naver.com/ks1st/products/5083908974"

date = '2021-08-03'

def crawl(url):
    url_elements = url.split('/')

    productNo, merchant = url_elements[-1], url_elements[-3]

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

    # print(script_bit, id_bit)
    # print(merchantNo, productNo)
    # exit()

    requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page=1&pageSize=20&merchantNo={0}&originProductNo={1}&sortType=REVIEW_CREATE_DATE_DESC'.format(merchantNo, productNo)
    response = requests.get(requests_url)
    
    if response.text == 'OK':
        return

    json = response.json()

    total_page = json['totalPages']

    index = 0
    df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

    for page in tqdm(range(1, total_page+1),ncols=100, desc=url_elements[-1]):

        requests_url = 'https://smartstore.naver.com/i/v1/reviews/paged-reviews?page={0}&pageSize=20&merchantNo={1}&originProductNo={2}&sortType=REVIEW_CREATE_DATE_DESC'.format(page, merchantNo, productNo)

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


    productNo = url_elements[-1]
    df.to_csv('request/{0}.csv'.format(productNo), encoding='utf-8-sig', mode='w')


if __name__ == "__main__":

    # url = pd.read_csv("lilydress/ss_urls.csv")
    # url = pd.read_csv("coively/urls.csv")
    # url = list(url['0'])

    # for i in url:
    #     crawl(i)
    crawl("https://brand.naver.com/melkin/products/581155411")
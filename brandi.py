import requests
import pandas as pd
from datetime import datetime, timedelta
import time

from requests.models import HTTPBasicAuth


def crawl(url, date):
    
    url = "https://cf-api-v2.brandi.me/v2/web/products/38042677/reviews?version=2101&limit=100&offset=200&tab-type=all"

    # response = requests.options(url)
    response = requests.get(url, headers={'Authorization': '3b17176f2eb5fdffb9bafdcc3e4bc192b013813caddccd0aad20c23ed272f076_1423639497'})
    # if response.status_code == 401:
    #     response = requests.get("https://cf-api-v2.brandi.me/v2/web/products/38042677/reviews?version=2101&limit=5&offset=0&tab-type=all", auth=HTTPBasicAuth('user', 'pass'))

    print(response.text)
    print(len(response.json()['data']))
    
if __name__ == "__main__":

    date = '2021-07-09'

    url = ""
    crawl(url, date)



# https://cf-api-v2.brandi.me/v2/web/products/35149663/reviews?version=2101&limit=5&offset=0&tab-type=all
# https://cf-api-v2.brandi.me/v2/web/products/35149663/reviews?version=2101&limit=5&offset=5&tab-type=all
# https://cf-api-v2.brandi.me/v2/web/products/35149663/reviews?version=2101&limit=5&offset=10&tab-type=all
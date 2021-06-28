from numpy import product
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep

url = ""
driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get(url) 

review_xpath = "/html/body/div/div/div[2]/div[2]/div[5]/div[1]/div/ul/li[3]/a"
recent_xpath = "/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/div[1]/div[1]/ul/li[2]"


driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

element = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath(review_xpath))
ActionChains(driver).move_to_element(element).click(element).perform()
sleep(1)

element = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath(recent_xpath))
ActionChains(driver).move_to_element(element).click(element).perform()
sleep(1)

df = pd.DataFrame(columns=['작성자', '작성일', '평점', '상품옵션', '리뷰내용', '좋아요', '이미지'])

index = 0
page = 1
while True:
    num = 1
    element = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/ul/div[1]")
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    while True:
        try:
            review = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/ul/div[{0}]".format(str(num)))
        except:
            break

        info = review.text
        info_list = list(info.split('\n'))

        content = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/ul/div[{0}]/div/div/div/div[1]/div/div[1]/div[2]/div/span".format(str(num))).text
        try:
            product_options = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/ul/div[{0}]/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[3]".format(str(num))).text
        except:
            product_options = ''
        if '평점' in info_list[0]:
            star  = info_list[1]
            id = info_list[2]
            date = info_list[3]
            like = info_list[-1]
            img = ''
        else:
            star  = info_list[2]
            id = info_list[3]
            date = info_list[4]
            like = info_list[-1]
            html = review.get_attribute('innerHTML')
            img = list({x.split('?')[0] for x in list(html.split('"')) if ".jpeg" in x or ".png" in x})

        df.loc[index] = [id, date, star, product_options, content, like, img]

        index += 1
        num += 1
    
    try:
        if page < 7:
            page += 1
        next_page = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div[5]/div[5]/div/div[3]/div/div[2]/a[{0}]".format(str(page+1))).click()
    except:
        break
driver.close()
# print(df)
df.to_csv('output.csv', encoding='utf-8-sig', mode='w')
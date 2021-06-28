from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import selenium
import pandas as pd
import time

url = "https://shopping.naver.com/style/style/home"

df = pd.DataFrame(columns=["url"])

options = webdriver.ChromeOptions()
# options.add_argument('window-size=1920x1080')
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)
driver.get(url)
time.sleep(1)
d = []
for i in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    element = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]")
    driver.execute_script('arguments[0].scrollIntoView(true);', element)

    a = element.get_attribute('outerHTML')

    b= a.split('"')
    c = [x for x in b if '/style/style/stores' in x]

    # for i in c:
    #     print('https://shopping.naver.com'+i)
    # print(len(c))
    for i in c:
        d.append(i)
d = set(d)
print(len(d))

# df.to_csv('urls.csv', encoding='utf-8-sig', mode='w')
driver.close()
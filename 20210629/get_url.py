from selenium import webdriver
import pandas as pd
import time

url = "https://shopping.naver.com/style/style/home"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)
driver.get(url)
time.sleep(0.9)
d = []
for i in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    element = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]")
    driver.execute_script('arguments[0].scrollIntoView(true);', element)

    a = element.get_attribute('outerHTML')

    b= a.split('"')
    c = ['https://shopping.naver.com' + x for x in b if '/products/' in x]

    for i in c:
        d.append(i)
d = set(d)
print(len(d))
df = pd.DataFrame(d)
print(df)

df.to_csv('urls.csv', encoding='utf-8-sig', mode='w')
driver.close()
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from time import *

url = "https://smartstore.naver.com/lilydress"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("headless")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(3)
driver.get(url)

element = driver.find_element_by_css_selector("#container > div._1XbSLEY_rb > div > div.kKWaaZzr6M > div > div > div._1AJ8D2PjS4._3nO3wKj4-Z > div > ul._3AV7RVieRB > li:nth-child(1)")
# driver.execute_script('arguments[0].scrollIntoView(true);arguments[0].click();', element)
ActionChains(driver).move_to_element(element).click(element).perform()

urls = []
page = 1

while True:
    for num in range(1,41):
        element = driver.find_element_by_css_selector("#CategoryProducts > ul > li:nth-child({0})".format(num))
        aa = element.get_attribute('outerHTML').split('"')
        for i, data in enumerate(aa):
            if '/products/' in data:
                link = 'https://smartstore.naver.com' + data
                break
        urls.append(link)
    page += 1
    try:
        next_page = WebDriverWait(driver, 3, poll_frequency=0.05).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#CategoryProducts > div._1HJarNZHiI._2UJrM31-Ry._3F77jPGGAN > a:nth-child({0})".format(str(page+1)))))
    except:
        try:
            next_page = WebDriverWait(driver, 3, poll_frequency=0.05).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#CategoryProducts > div._1HJarNZHiI._2UJrM31-Ry._3F77jPGGAN > a.fAUKm1ewwo._2Ar8-aEUTq")))
        except:
            break
        if '다음' in next_page.text:
            page = 1
        else:
            break
    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
    sleep(0.5)

df = pd.DataFrame(urls)
df.to_csv('ss_urls.csv', encoding='utf-8-sig', mode='w')

driver.close()
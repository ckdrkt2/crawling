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

categori_xpath = "/html/body/div/div/div[2]/div[2]/div[5]/div[1]/div/ul"

categoris = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath(categori_xpath)).text.split('\n')

for index in range(len(list(categoris))):
    if 'ë¦¬ë·°' in categoris[index]:
        element = driver.find_element_by_xpath(categori_xpath + "/li[{}]".format(str(index+1)))
        break

ActionChains(driver).move_to_element(element).click(element).perform()
sleep(1)

# ìµœì‹ ?ˆœ ?´ë¦?
element = WebDriverWait(driver, 10).until(lambda x:x.find_element_by_css_selector('#REVIEW > div > div.hmdMeuNPAt > div > div._1TvkeQbpJb > div._20Q8mCxsy- > ul > li:nth-child(3)'))
ActionChains(driver).move_to_element(element).click(element).perform()
sleep(1)
num = 1
review = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num)))

info = review.text
info_list = list(info.split('?Œë§¤ìž')[0].split('\n'))

like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child(1) > div > div.KHHDezUtRz > div > div._3w28SVZeZM").text
print(like)

content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
try:
    product_options = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div._3iYCagsFsO > div._301WLm00sr > div._31mfFx_-xd".format(str(num))).text
except:
    product_options = ''
print(info_list)
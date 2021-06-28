from multiprocessing import Process
from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from time import time

url = ['' for i in range(8)]
url[0] = ""
url[1] = ""
url[2] = ""
url[3] = ""
url[4] = ""
url[5] = ""
url[6] = ""
url[7] = ""

def crawl(url):

    start_time = time()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(3)
    driver.get(url)

    name = driver.find_element_by_css_selector("#INTRODUCE > div > div._1Hbih69XFT > div:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > b").text

    categori_css = "#content > div._2XqUxGzKDE > div._18UpKGc_hB > div > ul"
    
    # Î¶¨Î∑∞ Ïπ¥ÌÖåÍ≥†Î¶¨ ?Å¥Î¶?
    categoris = WebDriverWait(driver, 10, poll_frequency=0.1).until(lambda x:x.find_element_by_css_selector(categori_css)).text.split('\n')
    
    for index in range(len(list(categoris))):
        if 'Î¶¨Î∑∞' in categoris[index]:
            element = driver.find_element_by_css_selector(categori_css + " > li:nth-child({})".format(str(index+1)))
            break
       
    ActionChains(driver).move_to_element(element).click(element).perform()

    # ÏµúÏã†?àú ?Å¥Î¶?
    element = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#REVIEW > div > div.hmdMeuNPAt > div > div._1TvkeQbpJb > div._JEL2FoNN4 > ul > li:nth-child(2)')))
    # driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", element)
    ActionChains(driver).move_to_element(element).click(element).perform()
    sleep(0.5)

    df = pd.DataFrame(columns=['?ûë?Ñ±?ûê', '?ûë?Ñ±?ùº', '?èâ?†ê', '?ÉÅ?íà?òµ?Öò', 'Î¶¨Î∑∞?Ç¥?ö©', 'Ï¢ãÏïÑ?öî', '?ù¥ÎØ∏Ï??'])

    # ?ù¥ÎØ∏Ï?? url
    index = 0
    while True:
        num = 1

        while True:
            try:
                info = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                info = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0})".format(str(num))).text
            except:
                break
            
            info_list = list(info.split('\n'))

            try:
                content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                content = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div.eBQ2qaKgOU".format(str(num))).text
            try:
                like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div.KHHDezUtRz > div > div._3w28SVZeZM".format(str(num))).text
            except selenium.common.exceptions.StaleElementReferenceException:
                sleep(0.5)
                like = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div.KHHDezUtRz > div > div._3w28SVZeZM".format(str(num))).text
            # ?òµ?Öò 
            try:
                product_options = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > div > div._3AZFu4SXct > div > div._2hmOjCcGBh > div._3iYCagsFsO > div._301WLm00sr > div._31mfFx_-xd".format(str(num))).text
            except:
                product_options = ''
            
            # ?Ç¨Ïß? ?óÜ?ùå
            if '?èâ?†ê' in info_list[0]:
                star  = info_list[1]
                id = info_list[2]
                date = info_list[3]
                img_url = ''
                # print(index, id, info_list[0])
            # ?Ç¨Ïß? ?ûà?ùå
            else:
                star  = info_list[2]
                id = info_list[3]
                date = info_list[4]
                # print(index, id, info_list[0])
                # ?Å¥Î¶? ?êòÎ©¥ÏÑú ?ù¥ÎØ∏Ï?? ?è¨?ï®
                if '?ù¥ÎØ∏Ï?? ?éºÏ≥êÎ≥¥Í∏?' in info_list:
                    # ?çîÎ≥¥Í∏∞ ?Å¥Î¶?
                    # more = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))
                    more = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > a".format(str(num)))))
                    driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", more)
                    sleep(0.1)

                    # ?ù¥ÎØ∏Ï?? url ????û•
                    img = driver.find_element_by_css_selector("#REVIEW > div > div.hmdMeuNPAt > div > ul > div:nth-child({0}) > div > div > ul".format(str(num)))
                    html = img.get_attribute('outerHTML')
                    lst = list(html.split('"'))
                    img_url = list({x.split('?')[0] for x in lst if 'https' in x})
                # ?Å¥Î¶? ?êòÎ©¥ÏÑú ?ù¥ÎØ∏Ï?? ÎØ∏Ìè¨?ï®
                else:
                    img_url = ''

            # ?ç∞?ù¥?Ñ∞?îÑ?†à?ûÑ?óê Ï∂îÍ??
            df.loc[index] = [id, date, star, product_options, content, like, img_url]

            index += 1
            num += 1
        
        
        next_page = WebDriverWait(driver, 10, poll_frequency=0.1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#REVIEW > div > div.hmdMeuNPAt > div > div._1QyrsagqZm._2w8VqYht7m > a._3togxG55ie._2_kozYIF0B")))
        # ?ã§?ùå Î≤ÑÌäº?ù¥ Î≥¥Ïùº Í≤ΩÏö∞
        if '?ã§?ùå' in next_page.text:
            driver.execute_script("arguments[0].scrollIntoView(true);arguments[0].click();", next_page)
            sleep(1)
            # print("next page")
        # ?ã§?ùå Î≤ÑÌäº?ù¥ ?ïà Î≥¥Ïùº Í≤ΩÏö∞
        else: break

    driver.close()

    print(name, 'runtime:', time() - start_time)

    df.to_csv('{}.csv'.format(name), encoding='utf-8-sig', mode='w')

if __name__ == '__main__':

    procs = []

    start = time()

    urls = []
    for j in range(3):
        for i in url:
            urls.append(i)

    for i, num in enumerate(urls):
        proc = Process(target=crawl, args=(num,))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    print('total runtime:', time() - start)
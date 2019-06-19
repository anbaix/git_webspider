from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import time
browser=webdriver.Chrome()
browser.maximize_window()
wait=WebDriverWait(browser,15)

def crawle(url,key,page):
    browser.get(url=url)
    try:
        print('下拉到最后')
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#offer60')))
        time.sleep(3)
    except :
        print('*'*30,'等待商品加载超时','*'*30,'\n\n\n')
    for item in get_products():
        print(item)
        save_to_mongo(item, key)
    if page>1:
        for page in range(2,page+1):
            print('*' * 30, '第',page,'页', '*' * 30, '\n\n\n')
            get_more_page(page)
            for item in get_products():
                print(item)
                save_to_mongo(item, key)

def get_more_page(page):
    page_input=browser.find_element_by_class_name('ui2-pagination-goto')
    page_input.clear()
    page_input.send_keys(page)
    button=browser.find_element_by_css_selector('.ui2-pagination-go')
    button.click()
    time.sleep(3)
    try:
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#offer20')))
    except :
        print('*'*30,'超时加载','*'*30,'\n\n\n')
    time.sleep(3)


def get_products():
    html=browser.page_source
    doc=pq(html)
    items=doc('.brh-rfq-item').items()
    index=0
    for item in items:
        index+=1
        title=item.find('.brh-rfq-item__subject a').text().split('\n')
        title=' '.join(title)
        detail_a=item.find('.brh-rfq-item__detail').text().split('\n')
        detail=''.join(detail_a[:2])
        date_posted=item.find('.brh-rfq-item__open-time').text().replace('Date Posted','').split(' ')
        date_posted_n=date_posted[0]
        date_posted_u=date_posted[1:]
        date_posted_unit=' '.join(date_posted_u)
        quantity=item.find('.brh-rfq-item__quantity-num').text()
        country=item.find('.brh-rfq-item__country').text().replace('Posted in','')
        purchaser=item.find('.next-tag-body').text()
        quote_left=item.find('.quote-left').text().replace('Quotes Left ','')
        #拼接json
        yield{
        'main_category':'Electronic Components & Supplies',
        'second_category': 'EL Products',
        'third_category': 'EL Products',
        'key_word': '150412',
        'title':title,
        'detail':detail,
        'date_posted_n':date_posted_n,
        'date_posted_unit': date_posted_unit,
        'quantity': quantity,
        'country': country,
        'purchaser': purchaser,
        'quote_left':quote_left}

    print(' (●ˇ∀ˇ●) '*5)
    print('一共%d条数据'%index)

import pymongo
client=pymongo.MongoClient()
db=client.alibaba
def save_to_mongo(item,key):
    #根据关键字动态存入相应的表
    collection=db[key]
    if item:
        collection.insert(item)
        print('成功存储到mongo')
def main():
    url = 'https://sourcing.alibaba.com/rfq_search_list.htm?spm=a2700.8073608.1998677539.17.6d1e65aacOeDre&categoryIds=150412'
    key_words='source_category'
    page=int(1)
    crawle(url,key_words,page)

main()

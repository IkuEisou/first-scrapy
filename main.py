import requests
import csv
import time
import datetime
from bs4 import BeautifulSoup
from urllib import parse
from selenium import webdriver
from goose3 import Goose
from selenium.webdriver import ChromeOptions
# from selenium.webdriver.common.keys import Keys

domain = ""
# jp_lang = "&hl=ja&gl=JP&ceid=JP:ja"
en_lang = "&hl=en-US&gl=US&ceid=US:en"
comp = "sony"
if ' ' in comp:
    keywords = comp.split(' ')[0:-1]
    kws = ''
    for kw in keywords:
        kws += ' ' + kw
else:
    kws = comp
keyword = parse.quote(comp.encode('utf8'))
domain = parse.quote((" inurl:"+domain).encode('utf8'))
num = 10
url = 'https://news.google.com/rss/search?q="' + \
    keyword + '"' + domain + en_lang
res = requests.get(url)
news_list = []
option = ChromeOptions()
option.add_argument('start-maximized')
option.add_argument('disable-infobars')
option.add_argument('--disable-extensions')
# browser = webdriver.Chrome(options=option)
browser = webdriver.Firefox()

if res.status_code == 200:
    content = res.content
    soup = BeautifulSoup(content, "xml")
    items = soup.findAll('item')
    cnt = 1
    for item in items:
        if cnt > num:
            break

        title = item.title.text
        link = item.link.text
        summary = item.description.text
        news_from = item.source.text
        pubDate = item.pubDate.text

        # browser = webdriver.Chrome(options=option)
        # script = '''
        # Object.defineProperty(navigator, 'webdriver', {
        #     get: () => undefined
        # })
        # '''
        # browser.execute_cdp_cmd(
        #     "Page.addScriptToEvaluateOnNewDocument", {"source": script})
        browser.get(link)
        # cookie = browser.get_cookies()
        # print(cookie)
        time.sleep(3)
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        page = browser.page_source
        s2 = BeautifulSoup(page, 'lxml')
        contents = s2.body.find_all('p')
        g = Goose()
        article = g.extract(raw_html=page)
        text = article.cleaned_text
        kws = kws.strip()
        if kws not in text.lower():
            found = False
            for content in contents:
                if kws in content.text:
                    if found == False:
                        text = content.text
                        found = True
                    else:
                        text += '\n' + content.text
            if found == False:
                # browser.close()
                continue
        cnt += 1
        # browser.close()
        news_list.append({
            "news_title": title,
            "news_link": link,
            "news_text": text,
            "news_from": news_from,
            "pubDate": pubDate
        })
browser.close()
if len(news_list) > 0:
    keys = news_list[0].keys()
    now = datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")
    with open(kws+'_news@'+now+'.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(news_list)

import requests
from bs4 import BeautifulSoup
from urllib import parse
from fake_useragent import UserAgent
from selenium import webdriver
from goose3 import Goose
import csv
import time

comp = "NPC International Inc"
keywords = comp.split(' ')[0:-1]
kws = ''
for kw in keywords:
    kws += ' ' + kw
keyword = parse.quote(comp.encode('utf8'))
num = 10
url = "https://news.google.com/rss/search?q=" + \
    keyword + "&hl = en-US & gl = US & ceid = US: en"
res = requests.get(url)
news_list = []

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

        browser = webdriver.Chrome()
        script = '''
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        '''
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": script})
        browser.get(link)
        time.sleep(1)
        page = browser.page_source
        s2 = BeautifulSoup(page, 'lxml')
        contents = s2.body.find_all('p')
        g = Goose()
        article = g.extract(raw_html=page)
        text = article.cleaned_text

        if kws not in text:
            found = False
            for content in contents:
                if kws in content.text:
                    if found == False:
                        text = content.text
                        found = True
                    else:
                        text += '\n' + content.text
            if found == False:
                continue
        cnt += 1
        browser.close()
        news_list.append({
            "news_title": title,
            "news_link": link,
            "news_text": text,
            "news_from": news_from,
            "pubDate": pubDate
        })

if len(news_list) > 0:
    keys = news_list[0].keys()
    with open('news.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(news_list)

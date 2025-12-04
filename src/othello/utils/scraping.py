import requests
import os
import time
import sys
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

BASE_URL = "https://www.ffothello.org"
URL = BASE_URL + "/informatique/la-base-wthor/"
PATH = "wthor"

def get_html(url):
    try:
        res = requests.get(url, timeout=3)
        res.raise_for_status()
    except RequestException as e:
        print("Error:", e)
        sys.exit()
    time.sleep(2)
    return res

res = get_html(URL)
soup = BeautifulSoup(res.text, "html.parser")
ul_tags = soup.select("div.bkp-frame ul")
file_urls = []
for li_tag in ul_tags[1].select("li"):
    a_tag = li_tag.select("a")[0]
    file_urls.append(a_tag.get("href"))

for file_url in file_urls:
    url = BASE_URL + file_url
    res = get_html(url)
    name = os.path.basename(file_url)
    path = os.path.join(PATH, name)
    with open(path, "wb") as file:
        for chunk in res.iter_content(100000):
            file.write(chunk)
            file.flush()

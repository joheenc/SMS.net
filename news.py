from newsapi import NewsApiClient
import requests
import json
import urllib.request as urllib
import re

# Init
newsapi = NewsApiClient(api_key = '')

def getNews(query):
    userdata = {'q':query, 'apiKey': ''}
    reponse = requests.get('https://newsapi.org/v2/top-headlines?', params=userdata)
    reponse = reponse.json()

    searchResults = []
    for i in range(3):
        searchResults.append({"title" : reponse['articles'][i]["title"],
            "source" : reponse['articles'][i]['source']['name'],
            "preview" : reponse['articles'][i]["description"],
            "url" : reponse['articles'][i]["url"]})


def urlToParagraphs(url):
    try:
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
        req = urllib.Request(url, headers=headers)
        resp = urllib.urlopen(req)
        respData = resp.read()
        paragraphs = re.findall(r'<p>(.*?)</p>', str(respData))
        parsed = []

        for para in paragraphs:
            a = re.sub(r'\<[^>]*\>', '', para)
            b = re.sub(r'&#9.*?93;', '', a)
            b = re.sub(r'\\', '', b)
            c  = b.replace('\\n', '')
            parsed.append(c)
        return parsed

    except Exception as e:
        print(str(e))
        return []

#result = getNews('bitcoin')
#result =urlToParagraphs(#insert user input)

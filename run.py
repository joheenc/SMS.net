from flask import Flask, request, redirect
import json
import requests
import re
from html.parser import HTMLParser
from google.cloud import translate
import urllib.request as urllib
from twilio.twiml.messaging_response import Message, MessagingResponse
from newsapi import NewsApiClient

app = Flask(__name__)

statcode = 0
statholder = 0
searchRes = []
newsRes = []

@app.route("/sms", methods=['GET', 'POST'])
def sms():
    resp = MessagingResponse()
    message = request.form['Body']
    global statcode
    global statholder
    global searchRes
    global newsRes

    if statcode == 0: #entry point
        if "smsnet" in message.lower():
            resp.message("Welcome to SMSnet! Which of the following basic internet functions would you like to use?\n1) Search\n2) Maps\n3) News\n4) Translate")
            return str(resp)
        else:
            try:
                statcode = int(message)
                respStr = "Ok, enter your query for "
                if statcode == 1:
                    respStr += "search."
                elif statcode == 2:
                    respStr += "maps."
                elif statcode == 3:
                    respStr += "news."
                elif statcode == 4:
                    respStr += "translate (include desired language, comma-separated)."
                else:
                    respStr = "Bad request, please try again."
                    statcode = 0
            except:
                respStr = "Request error, please try again."
                statcode = 0
            resp.message(respStr)

    
    elif statcode == 1: #search
        if statholder == 0:
            searchRes, respStr = searchResults(message)
            resp.message(respStr + "\n\nFor the next 3 results, reply 'next'.")
            statholder = 100
            return str(resp)
        elif statholder == 100: #search option
            try:
                statholder = int(message)
                urlParas = urlToParagraphs(searchRes[statholder-1]["url"])
                respStr = urlParas[0] + "\n\nFor the next paragraph, reply 'next'."
            except:
                respStr = "Error parsing search string, please try again"
            resp.message(respStr)
            statcode = 0
            statholder = 0
            return str(resp)


    elif statcode == 2: #maps
        directions, respStr = getDirections(message)
        resp.message(respStr)
        statcode = 0
        statholder = 0
        return str(resp)

    elif statcode == 3: #news
        if statholder == 0:
            newsRes, respStr = getNews(message)
            resp.message(respStr + "\n\nFor the next 3 results, reply 'next'.")
            statholder = 100
            return str(resp)
        elif statholder == 100: #search option
            #try:
            statholder = int(message)
            urlParas = urlToParagraphs(newsRes[statholder-1]["url"])
            respStr = urlParas[0] + "\n\nFor the next paragraph, reply 'next'."
            #except:
                #respStr = "Error parsing search string, please try again"
            resp.message(respStr)
            statcode = 0
            statholder = 0
            return str(resp)


    elif statcode == 4: #translate
        translate_client = translate.Client()
        translateMsg = message.split(',')[0]
        translateLang = message.split(',')[1].strip()



def searchResults(query):
    #Searches Google

    searchResultsStr = json.loads(r.text)["items"]
    searchResults = []
    for i in range(3):
        searchResults.append({"title" : searchResultsStr[i]["title"],
            "website" : searchResultsStr[i]["displayLink"],
            "snippet" : searchResultsStr[i]["snippet"],
            "url" : searchResultsStr[i]["formattedUrl"]})

    c = 1
    responseStr = ""
    for item in searchResults:
        responseStr += str(c) + ") "
        responseStr += "'" + item["title"] + "':\n" + item["snippet"].strip('\n') + "\n(" + item["website"] + ')\n'
        responseStr += "\n"
        c += 1
    return searchResults, responseStr


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
            c = b.rstrip("\r\n")
            parsed.append(c)
        return parsed

    except Exception as e:
        print(str(e))
        return []


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        if self.get_starttag_text() == '<div style="font-size:0.9em">':
            self.fed.append(' ('+d+')')
        else:
            self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()



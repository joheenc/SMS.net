from flask import Flask, request, redirect
import json
import requests
import re
from html.parser import HTMLParser
from google.cloud import translate, vision
from google.cloud.vision import types
import urllib.request as urllib
from twilio.twiml.messaging_response import Message, MessagingResponse
from newsapi import NewsApiClient
import io
import os

app = Flask(__name__)

statcode = -1
statholder = 0
botChoice = 0
searchRes = []
newsRes = []
imgTags = []

@app.route("/sms", methods=['GET', 'POST'])
def sms():
    resp = MessagingResponse()
    message = request.form['Body']
    global statcode
    global statholder
    global searchRes
    global newsRes
    global botChoice


    if statcode == -1:
        if 'smsnet' in message.lower():
            resp.message("Well met! It appears that I've been summoned!")
            statcode = 0
            return str(resp)

    if statcode == 0: #entry point
        if "e" in message.lower() or "o" in message.lower() or "a" in message.lower() or "i" in message.lower() or "u" in message.lower():
            resp.message("Welcome to SMSnet! Which of the following basic internet functions would you like to use?\n1) Search\n2) Directions\n3) News\n4) Translate\n5) Image recognition and search\n6) E-banking and finances\nOr, if you'd prefer, I could just tell you a random joke!")
            return str(resp)
        else:
            try:
                statcode = int(message)
                respStr = ""
                if statcode == 1:
                    respStr = "Cool! What are you looking to learn more about? Or, would you like me to show you something trending instead? (If so, say 'trending')"
                elif statcode == 2:
                    respStr = "Nice! Where are you planning to go? If you need a recommendation, I know a great restaurant nearby. (say 'food' for a nearby restaurant)"
                elif statcode == 3:
                    respStr = "Staying informed is great! What are you looking to catch up on? If you'd like, I could show you a hot news article. (say 'hot' for a popular topic)"
                elif statcode == 4:
                    respStr = "Exotic! What do you want to translate, and to which language? (say e.g. 'Good morning, ru'). If you're feeling adventurous, I could teach you to say 'Hello' in a random language! (say 'teach')"
                elif statcode == 5:
                    respStr = "Sure thing. Just send me an image and I'll try my best to identify it!"
                elif statcode == 6:
                    respStr += "Serious business today! Here's how I can help--would you like:\n1) Directions to nearest ATM\n2) View your accounts\n3) View your transfers\n4) Open a new account"
                else:
                    respStr = "Okay, here's a good one. What is a chatbot's favorite article of clothing?"
                    statcode = 7
            except:
                respStr = "Request error, please try again."
                statcode = 0
            resp.message(respStr)
            return str(resp)
    
    elif statcode == 1: #search
        if 'trending' in message.lower():
            message = 'League of Legends world championship'
        if statholder == 0:
            searchRes, respStr = searchResults(message)
            resp.message("Search results for " + message + '\n\n' + respStr + "\n\nFor the next 3 results, reply 'next'.")
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
        if 'food' in message.lower():
            message = 'RU Hungry'
        directions, respStr = getDirections(message)
        resp.message('Directions to ' + message + '\n\n' + respStr)
        statcode = 0
        statholder = 0
        return str(resp)

    elif statcode == 3: #news
        if 'hot' in message.lower():
            message = 'Hong Kong'

        if statholder == 0:
            newsRes, respStr = getNews(message)
            resp.message('News related to ' + message + '\n\n' + respStr + "\n\nFor the next 3 results, reply 'next'.")
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
        if 'teach' in message.lower():
            message = 'Hello,sl'
        translate_client = translate.Client()
        translateMsg = message.split(',')[0]
        translateLang = message.split(',')[1].strip()
        translation = translate_client.translate(translateMsg, target_language = translateLang)
        language = "English"
        if translateLang == 'sl':
            language = "Slovenian"
        elif translateLang == 'es':
            language = "Spanish"
        elif transLateLang == 'ru':
            language = "Russian"
        respStr = "'" + translateMsg + "' in " + language + " is '" + translation['translatedText'] + "'"
        resp.message(respStr)
        statcode = 0
        statholder = 0
        return str(resp)

    elif statcode == 5: #images
        if statholder == 0:
            if request.values['NumMedia'] != '0':
                with open("/home/joheen_c/HackRUfall19/image.png", 'wb') as f:
                    image_url = request.values['MediaUrl0']
                    f.write(requests.get(image_url).content)

                img_client = vision.ImageAnnotatorClient()
                with io.open('/home/joheen_c/HackRUfall19/image.png', 'rb') as image_file:
                    content = image_file.read()

                image = types.Image(content=content)
                response = img_client.label_detection(image=image)
                labels = response.label_annotations

                respStr = "Here's what I see in your image:\n"
                for label in labels:
                    imgTags.append(label.description)
                    respStr += label.description + '\n'
                respStr += '\nWould you like to do an image search with this input? (y/n)'
                statholder = 99
                resp.message(respStr)
                return str(resp)
        elif statholder == 99:
            if 'y' in message.lower():
                searchRes, respStr = searchResults(imgTags[0] + ' ' + imgTags[1] + ' ' + imgTags[2])
                statholder = 100
                resp.message(respStr)
                return str(resp)
            else:
                resp.message('Ok, no image search was performed.')
                return str(resp)
        elif statholder == 100:
            statholder = int(message)
            urlParas = urlToParagraphs(searchRes[statholder-1]["url"])
            respStr = urlParas[0] + "\n\nFor the next paragraph, reply 'next'."
            resp.message(respStr)
            statcode = 0
            statholder = 0
            return str(resp)

    elif statcode == 6: #banking
        try:
            if statholder != -1:
                statholder = int(message)
        except:
            statholder = 0
            statcode = 0

        if statholder == 1:
            directions, dirStr = getATM(69, 420, 2)
            resp.message('Directions to your nearest ATM:\n\n' + dirStr + "\nContinue banking, or text SMSnet to return to main.")
        elif statholder == 2:
            resp.message(respStr)
        elif statholder == 3:
            resp.message(respStr)
        elif statholder == -1:
            accName = 'New Checking account'
            resp.message(accName + " created successfully!\nContinue banking, or text SMSnet to return to main.")
            statholder = 0
        elif statholder == 4:
            respStr = "What type of account would you like to open?\n1) Checking\n2) Savings\n3) Credit Card"
            resp.message(respStr)
            statholder = -1
        else:
            resp.message("Welcome to SMSnet! Which of the following basic internet functions would you like to use?\n1) Search\n2) Directions\n3) News\n4) Translate\n5) Image recognition and search\n6) E-banking and finances")
            return str(resp)
        
        return str(resp)

    elif statcode == 7: #joke
        resp.message("It's a hat. As in, cHAT-bot! It's hilarious, I swear.")
        statcode = 0
        return str(resp)


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

def getNews(query):
    reponse = requests.get('https://newsapi.org/v2/top-headlines?', params=userdata)
    reponse = reponse.json()

    searchResults = []
    for i in range(3):
        searchResults.append({"title" : reponse['articles'][i]["title"],
            "source" : reponse['articles'][i]['source']['name'],
            "preview" : reponse['articles'][i]["description"],
            "url" : reponse['articles'][i]["url"]})
    
    c = 1
    responseStr = ""
    for item in searchResults:
        responseStr += str(c) + ") "
        responseStr += "'" + item["title"] + "':\n" + item["preview"].strip('\n') + "\n(" + item["source"] + ')\n'
        responseStr += "\n"
        c += 1

    return searchResults, responseStr


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

def getDirections(dest):
    response = requests.get('https://maps.googleapis.com/maps/api/directions/json?', params=userdata)
    result = response.json()
    j=[]
    for i in range (0, len(result['routes'][0]['legs'][0]['steps'])):
        j.append(strip_tags(result['routes'][0]['legs'][0]['steps'][i]['html_instructions']))

    dirStr = ""
    for direction in j:
        dirStr += direction + '\n'

    return j, dirStr

#Returns the directions to the atm in an array
def getATM(lat, longi, rad):
    userdata = {'lat':38.9283, 'lng':-77.1753, 'rad':rad, 'key':key}
    reponse = requests.get('http://api.reimaginebanking.com/atms?', params=userdata)
    result = reponse.json()
    ret = []
    ret.append(result['data'][0]['geocode'])
    ret.append(result['data'][0]['address'])
    directions, dirStr = getDirectionsFour(0,0,ret[0]['lat'], ret[0]['lng'])
    return directions, dirStr


def getDirectionsFour(lat, longi, destlat, destlng):
    response = requests.get('https://maps.googleapis.com/maps/api/directions/json?', params=userdata)
    result = response.json()
    j=[]
    for i in range (0, len(result['routes'][0]['legs'][0]['steps'])):
        j.append(strip_tags(result['routes'][0]['legs'][0]['steps'][i]['html_instructions']))

    dirStr = ""
    for direction in j:
        dirStr += direction + '\n'
    return j, dirStr

#returns -1 if no user is found with the ID, else returns json object
def getCustomer(userId):
    userdata = {'key':key}
    response = requests.get('http://api.reimaginebanking.com/customers/' + str(userId), params=userdata)
    if response.status_code == 404:
        return -1
    result = response.json()
    return result

#returns -1 if no user is found, else return json object of all accounts associated with that user
#you can send the choosen account by parsing the json, else send all (requires user input)
def viewAllAcc(userId):
    if getCustomer(userId) == -1:
        return -1
    userdata = {'key':key}
    response = requests.get('http://api.reimaginebanking.com/customers/'+userId+'/accounts', params=userdata)
    result = response.json()
    retStr = ""
    for s in result:
        retStr += s['nickname'] + ": " + s['type'] + " account with balance $0 and rewards $0\n"
    return retStr

#creates an acc based on user input -1 means invalid user, -2 means invalid account type
#-3 means invalid params (very bad if this actually happens), 1 means nice
#valid account types are Credit Card, Savings, and Checking
def createAcc(userId ,accType, accName):
    if getCustomer(userId) == -1:
        return -1
    if accType != 'Credit Card' and accType != 'Savings' and accType != 'Checking':
        return -2
    userdata = {'type': accType, 'nickname':accName, 'rewards':0, 'balance':0}
    result = response.json()
    if result['code'] == 201:
        return 1
    else:
        return -3

#returns the account data with given id
def getAcc(accId):
    userdata = {'key':key}
    response = requests.get('http://api.reimaginebanking.com/accounts/'+accId+'?', params = userdata)
    if response.status_code == 404:
        return -1
    result = response.json()
    return result

#3 types of transfers views payer, payee, and both
#-2 is invalid transfer view type
def viewTrans(accId, transView = "Both"):
    if getAcc(accId) == -1:
        return -1
    if transView != "Both" and transView != "payer" and transView != "payee":
        return -2
    if transView == "Both":
        userdata = {'key':key}
    else:
        userdata = {'key':key, 'type':transView}
    reponse = requests.get('http://api.reimaginebanking.com/accounts/'+accId+'/transfers?', params = userdata)
    result = reponse.json()

    respStr = ""
    for s in result:
        respStr += s['description'] + ': ' + s["type"] + " transaction of $" + str(s['amount']) + ', on ' + str(s['transaction_date']) + '. Status: ' + s['status'] + '\n'

    return respStr


if __name__ == "__main__":
    app.run(debug=True)

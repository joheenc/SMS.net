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
newsapi = NewsApiClient(api_key = 'a5cdf10132df4cabaa04da5a39a3d103')

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

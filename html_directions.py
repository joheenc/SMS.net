import requests
import json
from html.parser import HTMLParser

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

def getDirections(lat, longi, dest):
    userdata = {'origin':str(40.502210)+','+str(-74.451950), 'destination':dest, 'key':'insert key here'}
    response = requests.get('https://maps.googleapis.com/maps/api/directions/json?', params=userdata)
    result = response.json()
    j=[]
    for i in range (0, len(result['routes'][0]['legs'][0]['steps'])):
        j.append(strip_tags(result['routes'][0]['legs'][0]['steps'][i]['html_instructions']))
    return j

import requests
import json
from html_directions import getDirections

#Returns the directions to the atm in an array
def getATM(lat, longi, rad):
    userdata = {'lat':38.9283, 'lng':-77.1753, 'rad':rad, 'key':''}
    reponse = requests.get('http://api.reimaginebanking.com/atms?', params=userdata)
    result = reponse.json()
    ret = []
    ret.append(result['data'][0]['geocode'])
    ret.append(result['data'][0]['address'])
    directions = getDirections(0,0,ret[0]['lat'], ret[0]['lng'])
    return directions

#result = getATM(0,0,1)
#print(*result, sep='\n')

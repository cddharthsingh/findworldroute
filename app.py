from flask import Flask, request
from flask_cors import CORS, cross_origin
import json
from haversine import haversine
import time
import data

app = Flask(__name__)
CORS(app, support_credentials=True)

cityList = {}
citiesByContinent = {
    "asia": [],
    "africa": [],
    "europe": [],
    "south-america": [],
    "north-america": [],
    "oceania": []
}

def getCityList():
    with open('city.json', 'r', encoding='ISO-8859-1') as j:
        global cityData 
        cityData = json.loads(j.read())
        for city in cityData:
            cityList[cityData[city]['id']] = {"name" : cityData[city]['name'], "id" : cityData[city]['id']}
            citiesByContinent[cityData[city]['contId']].append(cityData[city]['id'])

def getCityDistanceMatrix(citiesData):
    global cityDistanceMatrix
    cityDistanceMatrix = {}
    for city in citiesData:
        currentCityData = citiesData[city]
        mapping = {}
        loc = (currentCityData['location']['lat'], currentCityData['location']['lon'])
        for otherCity in citiesData:
            otherCityData = citiesData[otherCity]
            if (currentCityData['contId'] != otherCityData['contId']):
                otherLoc = (otherCityData['location']['lat'], otherCityData['location']['lon'])
                mapping[otherCityData['id']] = haversine(loc, otherLoc)
        cityDistanceMatrix[currentCityData['id']] = mapping

def getNextCity(coveredContinents, tripItinerary, distanceTraveled, nextContinents):
    lastCity = tripItinerary[-1]
    nextContinent = nextContinents[coveredContinents[-1]]
    nextCity = {}
    minDistance = 999999
    for city in citiesByContinent[nextContinent]:
        if cityDistanceMatrix[lastCity['id']][city] < minDistance:
            nextCity = cityData[city]
            minDistance = cityDistanceMatrix[lastCity['id']][city]
    coveredContinents.append(nextContinent)
    tripItinerary.append(nextCity)
    distanceTraveled.append(minDistance)

def getTripDetails(startCity):
    trips = []
    for i in range(0, 4):
        trip = {}
        coveredContinents = []
        tripItinerary = []
        distanceTraveled = []
        currentCityData = cityData[startCity]
        tripItinerary.append(currentCityData)
        coveredContinents.append(currentCityData['contId'])
        while len(coveredContinents) < 6:
            getNextCity(coveredContinents, tripItinerary, distanceTraveled, data.nextContinents[i])
        distanceTraveled.append(cityDistanceMatrix[tripItinerary[-1]['id']][startCity])
        tripItinerary.append(currentCityData)
        coveredContinents.append(currentCityData['contId'])
        trip['coveredContinents'] = coveredContinents
        trip['itinerary'] = tripItinerary
        trip['distanceTraveled'] = distanceTraveled
        trip['totalDistance'] = sum(distanceTraveled)
        trips.append(trip)

        print ("coveredContinents", coveredContinents)
        print ("tripItinerary", json.dumps(tripItinerary))
        print ("distanceTraveled", distanceTraveled)
        print ("Total Distance", sum(distanceTraveled))
    return json.dumps(trips)


def initData():
    getCityList()
    getCityDistanceMatrix(cityData)
    print(json.dumps(cityDistanceMatrix))

@app.route("/citylist")
@cross_origin(supports_credentials=True)
def home():
    return cityList

@app.route("/gettrip", methods=['GET'])
@cross_origin(supports_credentials=True)
def getTrip():
    args = request.args
    getTripDetails(args["startCity"])
    return getTripDetails(args["startCity"])
    
if __name__ == "__main__":
    start_time = time.time()
    initData()
    print("--- %s seconds ---" % (time.time() - start_time))
    app.run(debug=True)
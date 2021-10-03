import json
import requests
import numpy
import datetime
import os
import numpy as np

class TicketMaster:
    
    def __init__(self):
        try:
            
            self.placeInfoDict = np.load('data/placeInfoDict.npy',allow_pickle='TRUE').item()
            self.IDToPlaceName = np.load('data/IDToPlaceName.npy',allow_pickle='TRUE').item()

        except:
            self.placeInfoDict, self.IDToPlaceName = self.getAllSeatsDict()
            if(not os.path.exists("data")):
                os.makedirs('data')
            np.save('data/placeInfoDict.npy', self.placeInfoDict) 
            np.save('data/IDToPlaceName.npy', self.IDToPlaceName) 
    
    def getAllSeatsDict(self, gameID = '31005B2A0984366E'):
        
        urlPlace = "https://mapsapi.tmol.io/maps/geometry/3/event/"+gameID+"/placeDetailNoKeys?systemId=HOST&useHostGrids=true&app=CCP&sectionLevel=true"
        rplace = json.loads(requests.get(urlPlace).text)['pages'][0]["segments"]
        
        placeDict = {}
        IDToPlaceName = {}
        for section in rplace:
            for row in section['segments'][0]['segments']:
                for seat in row['placesNoKeys']:
                    ID = seat[0]
                    ligne = row['name']
                    colonne = seat[1]
                    coords = [seat[2], seat[3]]
                    section_name = section['name']
                    placeDict[section_name+'-'+ligne+colonne] = {'ticketMasterID':ID,
                                                                 'section': section_name,
                                                                 'row': ligne,
                                                                 'colonne':colonne,
                                                                 'coords': coords}
                    IDToPlaceName[ID] = section_name+'-'+ligne+colonne
        return placeDict, IDToPlaceName
    

    def getNextMaches(self, ):
        startDate = datetime.date.today().strftime("%Y-%m-%d")
        endDate =(datetime.date.today()+datetime.timedelta(weeks=4*3)).strftime("%Y-%m-%d")
        
        
        url = "https://statsapi.web.nhl.com/api/v1/schedule?site=fr_nhlCA&startDate="+startDate+"&endDate="+endDate+"&teamId=8&expand=schedule.teams,schedule.venue,schedule.metadata,schedule.ticket,schedule.broadcasts.all"
        t = requests.get(url)
        r = json.loads(t.text)
    
        matchDict = []
        for event in r['dates']:
            date = event['date']
            if(event['games'][0]['teams']['home']['team']['name'] == 'Canadiens de Montréal'):
                tlink = event['games'][0]['tickets'][0]["ticketLink"]
                gameID = tlink.split("?")[0].split('/')[-1]
                ennemy = event['games'][0]['teams']['away']['team']['name']
                matchDict+= [{"date": date,
                               "opposingTeam": ennemy,
                               "ticketMasterGameID": gameID,
                               "ticketMasterURL": tlink,
                                   }]
        return matchDict

    def seatKeysToArray(self, key, ante = ""):
        i=0
        while(i < len(key) and key[i] != '['):
            ante += key[i]
            i+=1
        internal = []
        temp = ""
        state = 0
        for l in key[i+1:-1]:
            if(l == '['):
                temp += l
                state += 1
            elif(l == ']'):
                temp += l
                state -= 1
            elif(l ==',' and state ==0):
                internal += [temp]
                temp = ''
            else:
                temp += l
        if(temp != ""):
            internal += [temp]
        else:
            return [ante]
        
        listPlaces = []
        for text in internal:
            r = TicketMaster.seatKeysToArray(text, ante = ante)
            if(isinstance(r, list)):
                listPlaces += r
            else:
                listPlaces += [r]
        return listPlaces
            
            
        
    
    
    def getPricesFromID(self, gameID):
        urlPrice = "https://offeradapter.ticketmaster.com/api/ismds/event/"+gameID+"/facets?show=totalpricerange+places&by=offers&oq=not(locked)&q=available&apikey=b462oi7fic6pehcdkzony5bxhe&apisecret=pquzpfrfz7zd2ylvtz3w5dtyse&resaleChannelId=internal.ecommerce.consumer.desktop.web.browser.ticketmaster.ca"
        r2 = json.loads(requests.get(urlPrice).text)['facets']
        
        urlPlace = "https://mapsapi.tmol.io/maps/geometry/3/event/"+gameID+"/placeDetailNoKeys?systemId=HOST&useHostGrids=true&app=CCP&sectionLevel=true"
        rplace = json.loads(requests.get(urlPlace).text)['pages'][0]["segments"]
        
        placeDict = {}
        for p in rplace:
            section = p['name']
            for row in p['segments']:
                for w in row['segments']:
                    rowLetter = w['name']
                    for seat in w['placesNoKeys']:
                        key = seat[0]
                        number = seat[1]
                        xloc = seat[2]
                        yloc = seat[3]
                        placeDict[key] = {"section": section,
                                          "row": rowLetter,
                                          "number": number,
                                          "coords": [xloc,yloc]}
        
        availableTickets = []
        for ticketOffer in r2:
            if(len(ticketOffer['offers'])>0):
                seatsIDs = TicketMaster.seatKeysToArray(ticketOffer["places"][0])
                for s in seatsIDs:
                    seatInfo = placeDict[s]
                    seatInfo['price'] = ticketOffer['totalPriceRange'][0]['max']
                    availableTickets += [seatInfo]
            
        return availableTickets


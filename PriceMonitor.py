# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 17:21:36 2021

@author: arnau
"""
from TicketMaster import TicketMaster
import datetime
import numpy as np
import os


class PriceMonitor:
    
    
    
    def __init__(self):
        self.tm = TicketMaster()
        try:
            self.recordPrices = np.load('data/recordPrices.npy',allow_pickle='TRUE').item()
        except:
            self.recordPrices = {}
        
    def placeToInterrestCategory(self, seat):
        section = seat.split('-')[0]
        if(section[0] == '1'):
            cat = "1st ring"
            if((int(section) >= 110 and int(section) <=116) or (int(section) >= 122 or int(section)<=104)):
                cat += " - Centered"
            else:
                cat += " - Offside"
        elif(section[0] == '2'):
            cat = "2nd ring"
            if((int(section) >= 211 and int(section) <=215) or (int(section) >= 223 or int(section)<=203)):
                cat += " - Centered"
            else:
                cat += " - Offside"
        elif(section[0] == '3'):
            cat = "3rd ring"
            if((int(section) >= 316 and int(section) <=322) or (int(section) >= 334 or int(section)<=304)):
                cat += " - Centered"
            else:
                cat += " - Offside"
        elif(section[0] == '4'):
            cat = "4th ring"
            if((int(section) >= 416 and int(section) <=422) or (int(section) >= 434 or int(section)<=404)):
                cat += " - Centered"
            else:
                cat += " - Offside"
        return cat
                
    def update(self):
        self.updateNextMatches()
        for match in self.nextMatches:
            date = match['date']
            if(not date in self.recordPrices.keys()):
                self.recordPrices[date] = {}
            tickets = self.tm.getPricesFromID(match['ticketMasterGameID'])
            
            placesNeedingNotification = {}
            newBestPricesCat = []
            
            for (place, prix) in tickets.items():
                cat = self.placeToInterrestCategory(place)
                if(not cat in self.recordPrices[date]):
                    newBestPricesCat += [cat]
                    self.recordPrices[date][cat] = prix
                    placesNeedingNotification[cat] = [(place, prix)]
                elif(self.recordPrices[date][cat] == prix and cat in newBestPricesCat):
                    if(cat in placesNeedingNotification.keys()):
                        placesNeedingNotification[cat] += [(place, prix)]
                    else:
                        placesNeedingNotification[cat] = [(place, prix)]
                elif(self.recordPrices[date][cat] > prix):
                    newBestPricesCat += [cat]
                    self.recordPrices[date][cat] = prix
                    placesNeedingNotification[cat] = [(place, prix)]
        if(not os.path.exists("data")):
            os.makedirs('data')
            np.save('data/recordPrices.npy', self.recordPrices)                       

        
    def updateNextMatches(self):
        date = datetime.date.today().strftime("%Y-%m-%d")
        try:
            self.nextMatches = np.load('data/nextMatches.npy',allow_pickle='TRUE').item()[date]
        except:
            print("No files found which match up to date match status, going to scrap it")
            self.nextMatches = self.tm.getNextMaches()
            if(not os.path.exists("data")):
                os.makedirs('data')
            np.save('data/nextMatches.npy', {date:self.nextMatches}) 
        
        
        
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  6 17:21:36 2021

@author: arnau
"""
from TicketMaster import TicketMaster
from CentreBell import CentreBell
import datetime
import numpy as np
import os


class PriceMonitor:
    
    
    
    def __init__(self):
        self.tm = TicketMaster()
        self.cb = CentreBell()
        try:
            self.recordPrices = np.load('data/recordPrices.npy',allow_pickle='TRUE').item()
        except:
            print("No previous prices found")
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
                if(not cat in self.recordPrices[date].keys()):
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
            if(len(placesNeedingNotification.keys())>0):
                self.notify(placesNeedingNotification, match)
        if(not os.path.exists("data")):
            os.makedirs('data')
        np.save('data/recordPrices.npy', self.recordPrices)                       

    def notify(self, notifDict, match):
        text = ""
        placesToHighlight = []
        prices = []
        for cat, places in notifDict.items():
            text += cat + " : "+str(places[0][1])+"CAD\n"
            for p in places:
                placesToHighlight += [p[0]]
                prices += [p[1]]
        title = match['opposingTeam']+" - " + my_format(match['date'])
        self.cb.plotStadium(placesToHighlight, prices,outpath="outputs/"+match['date']+".png")
        print(title)
        print(text)
        print()
        
         
        
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
        

def my_format(ds):
    dt = datetime.datetime.strptime(ds, '%Y-%m-%d')
    return '{} {}'.format(dt.strftime('%A, %B'), ordinal(dt.day))

def ordinal(n):
    if 11 <= n <= 13:
        return '{}th'.format(n)
    if n%10 == 1:
        return '{}st'.format(n)
    elif n%10 == 2:
        return '{}nd'.format(n)
    elif n%10 == 3:
        return '{}rd'.format(n)
    else:
        return '{}th'.format(n)
        
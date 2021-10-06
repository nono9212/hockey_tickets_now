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
        
        
        
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 17:17:09 2021

@author: arnau
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import json
import requests
import matplotlib.colors

class CentreBell:
    
    def __init__(self):
        self.stadium = plt.imread('./img/stadium.png')
        plt.ioff()
        try:
            
            self.placeInfoDict = np.load('data/placeInfoDict.npy',allow_pickle='TRUE').item()
        except:
            self.placeInfoDict = self.getAllSeatsDict()
            if(not os.path.exists("data")):
                os.makedirs('data')
            np.save('data/placeInfoDict.npy', self.placeInfoDict)

    def getAllSeatsDict(self, gameID = '31005B2A0984366E'):
        
        urlPlace = "https://mapsapi.tmol.io/maps/geometry/3/event/"+gameID+"/placeDetailNoKeys?systemId=HOST&useHostGrids=true&app=CCP&sectionLevel=true"
        rplace = json.loads(requests.get(urlPlace).text)['pages'][0]["segments"]
        
        placeDict = {}
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
        return placeDict
    
    def plotStadium(self, seatsToHighlight=[], prices=None, outpath="outputs/test.png"):
        
        x = []
        y = []
        for s in list(self.placeInfoDict.keys()):
            c = self.placeInfoDict[s]['coords']
            x += [c[0]/10.0]
            y += [c[1]/10.0]
        fig, ax = plt.subplots()
        ax.set_axis_off()
        im      = ax.imshow(self.stadium)
        im = ax.scatter(x,y, s=0.5, c='w',edgecolors='grey', linewidth=0.2,alpha=0.7)
        x = []
        y = []
        for s in seatsToHighlight:
            c = self.placeInfoDict[s]['coords']
            x += [c[0]/10.0]
            y += [c[1]/10.0]
        if(prices == None):
            im = ax.scatter(x,y, s=40, c='#FF00FF')
        else:
            #cmap = plt.cm.rainbow
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","yellow","red"])
            norm = matplotlib.colors.Normalize(vmin=50, vmax=250)
            im = ax.scatter(x,y, s=40, c=cmap(norm(prices)),edgecolors="#FF00FF",linewidths=0.2)
        xmin, xmax = ax.get_xlim()
        ax.set_xlim(xmin-150,xmax+150)
        donePrices = []
        for xs,ys,ps in zip(x,y,prices):
            label = "{:.0f}$".format(ps)
            if(not ps in donePrices):
                donePrices+=[ps]
                ax.annotate(label, # this is the text
                             (xs,ys), # these are the coordinates to position the label
                             textcoords="offset points", # how to position the text
                             xytext=(-15,-2.5),
                             size=8,
                             ha='center') # horizontal alignment can be left, right or center
        fig.savefig(outpath,dpi=400, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        
        
        
        
        
        
        
        
        
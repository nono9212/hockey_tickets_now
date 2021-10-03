# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 17:17:09 2021

@author: arnau
"""

import matplotlib.pyplot as plt

class CentreBell:
    
    def plotStadium():
        stadium = plt.imread('./img/stadium.png')
        fig, ax = plt.subplots()
        im      = ax.imshow(stadium)
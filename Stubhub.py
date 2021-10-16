import requests
from requests_hawk import HawkAuth
import json
import urllib

class Stubhub:
    
    def __init__(self):
        self.headers = {
        'authority': 'www.stubhub.ca',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '^\\^Google',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '^\\^Windows^\\^',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'accept': 'application/json',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.google.com/',
        'accept-language': 'fr-FR,fr;q=0.9',
        }
        self.connect()

    def connect(self):
        response = requests.get('https://www.stubhub.ca/fr/', headers=self.headers)
        key = response.headers['Set-Cookie'].split("SH_BAU=")[1].split(';')[0]
        ids =json.loads(urllib.parse.unquote(key))
        self.hawk_auth = HawkAuth(id=ids['id'], key=ids['key'],always_hash_content=False)
    
    def  getNextMatches(self):
        url = "https://www.stubhub.ca/bfx/api/search/catalog/events/v3?shstore=8&status=active%20%7Ccontingent&spellCheck=true&boostByCategory=true&lang=true&includeNonEventEntities=true&edgeControlEnabled=true&fieldList=id%2CticketInfo%2Cdistance%2Cname%2CeventDateLocal%2Ccategories%2Cgroupings%2Cperformers%2Cvenue%2CeventInfoUrl%2CdisplayAttributes%2Cdescription%2CimageUrl%2CcreatedDate%2CperformersCollection%2CeventType%2CurgencyMessage%2CmetaInfo%2Cstatus&sourceId=0%20%7C1%20%7C4001%20%7C5001%20%7C29001&parking=false&point=45.50884%2C-73.58781&radius=50&excludeFromRadius=false&geoExpansion=false&start=0&rows=200&dateLocal=&sort=eventDateLocal%20asc&reRankBy=relevance&improvedRelevancy=true&eventType=Main%7CFestival%7CSeason%7CTailgate%7CHospitality&performerRole=homeTeam&performerId=7554"
        r = requests.get(url, auth=self.hawk_auth, headers=self.headers)
        j = json.loads(r.text)['events']
        eventIDstubhub = {}
        for e in j :
            eventIDstubhub[e["eventDateLocal"][:10]] = e["id"]
        return eventIDstubhub
    
    def getPrices(self, matchID):
        totalListings = 1
        start = 0
        available = {}
        while(start < totalListings):
            urlsh="https://www.stubhub.ca/bfx/api/search/inventory/v2/listings?additionalPricingInfo=true&allSectionZoneStats=true&edgeControlEnabled=true&eventLevelStats=true&eventPricingSummary=true&listingAttributeCategorySummary=true&pricingSummary=true&quantitySummary=true&sectionStats=true&shstore=1&start="+str(start)+"&urgencyMessaging=true&valuePercentage=true&zoneStats=true&scoreVersion=v2&eventId="+str(matchID)+"&quantity=&rows=60&sort=price%20asc%2C%20value%20desc&priceType=bundledPrice&listingAttributeCategoryList=&excludeListingAttributeCategoryList=&deliveryTypeList=&sectionIdList=&zoneIdList=&pricemin=&pricemax=&listingRows="
            rsh = requests.get(urlsh, auth=self.hawk_auth, headers=self.headers)
            stubhub = json.loads(rsh.text)
            totalListings = stubhub['totalListings']
            start += 60
            for l in stubhub['listing']:

                if(l['sectionName'][-3:].isnumeric()):
                    price = l['price']['amount']
                    section = int(l['sectionName'].split(' ')[-1]) 
                    rowseatcounts = {}
                    for s in l['seats']:
                        col = s['row']
                        if(col in rowseatcounts.keys()):
                            rowseatcounts[col] += 1
                        else:
                            rowseatcounts[col] = 1
                        siege = rowseatcounts[col]
                        name = str(section)+"-"+col+str(siege)
                        available[name] = l['price']['amount']
        return available
                    
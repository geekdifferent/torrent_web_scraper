#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import re
import json
import web_scraper_lib

webpage_addr = [
        "https://torrentgee16.com/board/torrent_ent?&page=",
        "https://torrentgee16.com/board/torrent_social?&page="
        ]

class site_scraper:
    def __init__(self, JD):
        self.sitename = "torrentgee"
        self.name = "web_scraper_06"
        self.mainUrl = "https://torrentgee16.com"
        self.JD = JD

        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))

    def saveNewLatestIDwithCate(self, category, newId):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentgee_kortv_ent = newId)
            self.kortv_ent_id = newId
        elif category == 'kortv_social':
            tmp.update(torrentgee_kortv_soc = newId)
            self.kortv_soc_id = newId
        else:
            print("Something Wrong, category = %s" % category)

        self.JD.set('history', tmp)
        return

    def needKeepGoing(self, category, id):
        tmp = None
        if category == 'kortv_ent':
            tmp = self.kortv_ent_id
        elif category == 'kortv_social':
            tmp = self.kortv_soc_id
        elif category == 'kortv_dra':
            tmp = self.kortv_dra_id
        elif category == "movie":
            tmp = self.movie_id
        else:
            print("Something Wrong, category = %s" % category)
            return False
        
        if id > tmp:
            return True

        return False

    def getMainUrl(self):
        return self.mainUrl

    def checkMainUrl(self):
        ret = web_scraper_lib.checkUrl(self.mainUrl)
        return ret

    def getName(self):
        return (self.name)

    def getScrapUrl(self, cateIdxNo, count):
        return (webpage_addr[cateIdxNo]+str(count))

    def getParseData(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('div', attrs={'class': 'list-wrap'}).find_all('a', href=re.compile(".*post.*"))
        return nameList

    #url을 기반으로 wr_id text를 뒤의 id parsing 
    def get_wr_id(self, url):

        tmp = url.rfind('post')
        if (tmp < 0): # 둘다 검색 못하면 포기
            return 0
        else:
            checkStr = 'post'
            #example: https://torrentgee16.com/post/49322?&page=1
            startp = tmp+len(checkStr)+1
            endp = startp

            for endp in range(startp,len(url)):
                if (url[endp]).isdigit():
                    continue
                else:
                    endp = endp-1
                    break

            endp = endp+1
        return int((url[startp:endp]))

    def getmagnetDataFromPageUrl(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnet = None
        if not bsObj == None:
            magnetItem = bsObj.find('a', onclick=re.compile(".*magnet.*"))
            if not magnetItem == None:
                _ = magnetItem.get('onclick')
                lcnt = _.find("'")
                rcnt = _.rfind("'")
                magnet = _[lcnt+1:rcnt]
                print(magnet)

        return magnet

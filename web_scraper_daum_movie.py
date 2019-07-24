#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import re
import json
import web_scraper_lib
import sys
import datetime

#태그에 의존적이므로 설정파일로 빼지 않음, 즉 변경의 의미가 없음
RANKING = 0
webpage_addr = ["https://movie.daum.net/boxoffice/monthly?yyyymm="]

class site_scraper:
    def __init__(self):
#, JD):

        today = datetime.date.today()
        first = today.replace(day=1)
        lastMonth = first - datetime.timedelta(days=1)

        webpage_addr[RANKING] += lastMonth.strftime("%Y%m")
        #print("info, site_scraper webpage_addr = %s" % webpage_addr)

        #self.sitename = "torrentwal"
        #self.name = "web_scraper_04"
        #self.mainUrl = "https://torrentwal.com"
        #self.JD = JD

        #self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        #self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))
        #self.kortv_dra_id = JD.get('history').get("%s_kortv_dra" % (self.sitename))

    def checkUrl(self):
        ret = web_scraper_lib.checkUrl(self.getScrapUrl())
        return ret

    def getScrapUrl(self):
        return (webpage_addr[RANKING])

    # 리스트의 url링크 리스트
    def getParseData(self):
        bsObj = web_scraper_lib.getBsObj(self.getScrapUrl())
        #print("info, getParseData bsObj = ", bsObj)
        nameList = bsObj.find_all('strong', attrs={'class' : 'tit_join'})
#.find_all('a',href=True)
        #print("info, getParseData nameList = ", nameList)
        return nameList


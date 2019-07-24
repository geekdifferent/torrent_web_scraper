#!/usr/bin/env python3

from datetime import datetime as dtime
import os
import sys
import web_scraper_lib
import web_scraper_daum_movie

__version__ = 'v1.00'


if __name__ == '__main__':

    SETTING_PATH = os.path.realpath(os.path.dirname(__file__))+"/"
    SETTING_FILE = SETTING_PATH+"web_scraper_settings.json"
    HISTORY_FILE = SETTING_PATH+"web_scraper_history.csv"
    MOVIE_TITLES = SETTING_PATH+"movie_titles.txt"
    runTime = dtime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print( "%s %s is going to work at %s. %s" % (os.path.basename(__file__),
    #    __version__, runTime, sys.getdefaultencoding()) )

    JD = web_scraper_lib.JsonParser(SETTING_FILE)

    scraper = web_scraper_daum_movie.site_scraper()

    #Step 1. test for access with main url
    #print("====================================\n=> Try to access site : ", scraper.getScrapUrl())

    if not scraper.checkUrl():
      #print("info, main scraper.checkUrl = false")
      sys.exit()

    title_tag_list = scraper.getParseData()
    # <strong class="tit_join"><a class="link_g #list #monthly @1" href="/moviedb/main?movieId=111292">기생충</a></strong>, ...
    #print("info, main titles_tag = ", titles_tag)

    file_name = SETTING_PATH+JD.get("movie").get("list")
    f = open(file_name, 'a', encoding="utf-8")

    for num, title_tag in enumerate(title_tag_list, start=1):

      title = title_tag.text
      print(title)

      f.write(title+"\n")

      if num == JD.get("movie").get("ranking"):
        break;

    f.close()

    sys.exit()

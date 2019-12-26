#!/usr/bin/env python3
from datetime import datetime as dtime
import os
import sys
import web_scraper_01
import web_scraper_02
import web_scraper_03
import web_scraper_04
import web_scraper_05
import web_scraper_lib

__version__ = 'v1.00'

if __name__ == '__main__':

    SETTING_PATH = os.path.realpath(os.path.dirname(__file__))+"/"
    SETTING_FILE = SETTING_PATH+"web_scraper_settings.json"
    HISTORY_FILE = SETTING_PATH+"web_scraper_history.csv"
    runTime = dtime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print("%s %s is going to work at %s. %s" % (os.path.basename(__file__),
    #    __version__, runTime,sys.getdefaultencoding()) )

    JD = web_scraper_lib.JsonParser(SETTING_FILE)
    MOVIE_LIST_FILE = SETTING_PATH+JD.get("movie").get("list")
    webpage_max = JD.get('page_scrwap_max')

    # This list is to scrap websites.
    siteList = []

    if JD.get('enable-torrentboza') == "True":
        siteList.append(web_scraper_01)
    if JD.get('enable-torrentmap') == "True":
        siteList.append(web_scraper_02)
    if JD.get('enable-torrentdal') == "True":
        siteList.append(web_scraper_03)
    if  JD.get('enable-torrentwal') == "True":
        siteList.append(web_scraper_04)
    if  JD.get('enable-torrentview') == "True":
        siteList.append(web_scraper_05)

    if len(siteList) == 0:
        print("Wrong, we should choice at least one analyzer.")
        sys.exit()

    for site in siteList:
        scraper = site.site_scraper(JD)

        #Step 1. test for access with main url
        #print("====================================\n=> Try to access site : ", scraper.getMainUrl())
        if not scraper.checkMainUrl():
            continue

        #Step 2. Iterate category for this site
        for cateIdx in web_scraper_lib.getCateList():

        #Step 3. setup Latest Id for this site/this category
            needNewLatestId = True
            #print("scraping [%s][%s]" % (scraper.sitename, cateIdx))

        #Step 4. iterate page (up to 10) for this site/this category
            for count in range(1, webpage_max+1):
                needKeepgoing = True
                cateIdxNo = web_scraper_lib.getCateIdxFromStr(cateIdx)
                url = scraper.getScrapUrl(cateIdxNo, count)
                boardList = scraper.getParseData(url)

                #print("info: url=%s" % url)

                #for board in boardList:
                for num, board in enumerate(boardList, start=1):
                    #print("info: board=%s" % board)
                    #게시판 제목
                    title = board.get_text().replace('\t', '').replace('\n', '')
                    href = board.get('href').replace('..', scraper.mainUrl)
                    #print("info: href=\t%s" % href)
                    boardIdNum = scraper.get_wr_id(href)
                    #print("[%d][%d] - %s" % (num, boardIdNum, title))

                    if needNewLatestId:
                        newLatestId = scraper.get_wr_id(href)
                        if newLatestId > 0:
                            #print("We set up for new latest ID %d." % newLatestId)
                            needNewLatestId = False
                        else:
                            print("Something wrong, cannot get new latest ID - %d." % newLatestId)

                    #boardList의 첫 게시물의 id를 확인
                    if num == 1:
                        if not (scraper.needKeepGoing(cateIdx, boardIdNum)):
                            needKeepgoing = False
                            #print("needKeepgoing is false --> break \tcateIdx=%s,boardIdNum=%s" % (cateIdx,boardIdNum))
                            break
                    if cateIdx =="movie":
                      matched_name = web_scraper_lib.checkTitleWithMovieList(title, MOVIE_LIST_FILE, \
                        JD.get("movie").get("video_codec"), JD.get("movie").get("resolution"), dtime.now().strftime("%Y") )
                    else:
                      matched_name=web_scraper_lib.checkTitleWithProgramList(title)

                    if not matched_name:
                        #print("info main matched_name ", title)
                        continue

                    if not (scraper.needKeepGoing(cateIdx, boardIdNum)):
                        needKeepgoing = False
                        #print("needKeepgoing2 --> break")
                        break

                    print("info: parse info=\t[%s][%s][%d][p. %d] - %s" % \
                            (scraper.sitename, cateIdx, boardIdNum, count, title))

                    magnet = scraper.getmagnetDataFromPageUrl(href)
                    #print("\t%s" % magnet)

                    #magnet was already downloaded.
                    if web_scraper_lib.check_magnet_history(HISTORY_FILE, magnet):
                        continue

                    if cateIdx =="movie":
                      download_dir=JD.get("movie").get("download")
                      if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    else:
                        if JD.get('enable-download-base') == "True":
                            download_dir=JD.get("download-base")+"/"+matched_name
                        else:
                            download_dir=""
                    #print(download_dir)

                    session_id = web_scraper_lib.get_session_id_torrent_rpc(JD)
                    web_scraper_lib.add_magnet_transmission_remote(magnet, JD, download_dir, session_id)

                    if cateIdx == "movie":
                      #movie_list에서 삭제하기
                      f = open(MOVIE_LIST_FILE, "r", encoding="utf-8")
                      lines = f.readlines()
                      buffer = ""
                      for line in lines:
                        #print("info, main matched_name = %s, line = %s" % (matched_name, line))
                        if not matched_name in line:
                          buffer += line
                        else:
                          print("info, main contain, matched_name = %s, line = %s" % (matched_name, line))
                      f.close()

                      f = open(MOVIE_LIST_FILE, "w", encoding="utf-8")
                      f.write(buffer)
                      f.close()
                    else:
                      web_scraper_lib.remove_transmission_remote(JD, session_id, matched_name)

                    web_scraper_lib.add_magnet_info_to_file(HISTORY_FILE,
                            runTime, scraper.sitename, title, magnet, matched_name)

                if not needKeepgoing:
                    break

        #Step 5. save scrap ID
            scraper.saveNewLatestIDwithCate(cateIdx, newLatestId)

    sys.exit()

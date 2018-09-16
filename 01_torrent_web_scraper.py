#!/usr/bin/python
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import re
import json

class JsonParser:
    def __init__(self, setfileName):
        self.JsonFile = setfileName
        try:
            dataFile = open(self.JsonFile, 'r')
        except FileNotFoundError as e:
            print(str(e))
            print("Please, set your file path.")
            exit()
        else:
            self.data = json.load(dataFile)
            dataFile.close()

    def get(self, key):
        return (self.data[key])

    def set(self, key, value):
        with open(self.JsonFile, 'w', encoding='utf-8') as dataFile:
            self.data[key] = value
            json.dump(self.data, dataFile, sort_keys = True, ensure_ascii=False, indent = 4)

def add_magnet_transmission_remote(magnet_addr):
    cmdArgs = 'transmission-remote %s -n %s:%s -a "%s"' % (JD.get('trans-port'), JD.get('trans-id'), JD.get('trans-pw'), magnet_addr)
    popen = subprocess.Popen(cmdArgs, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return

def getBsObj(addr):
    req = Request(addr, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read().decode('utf-8','replace')
    data = BeautifulSoup(html, "html.parser")
    return data

def url_download_torrent(urlWithTorrent):
    thisUrlId = get_wr_id(urlWithTorrent)

    if (url_check_post_id(thisUrlId)):
        print("\t===> download torrent : %s" % (urlWithTorrent))
        bsObj = getBsObj(urlWithTorrent)
        magnetList = bsObj.findAll("a", href=re.compile(".*magnet\:\?xt*")) #마그넷 정보 추출

        #실제로는 magnetList에는 1개만 있을 것임
        for magnet in magnetList:
            magnet_href = magnet['href']
            #print("magnet_href : ", magnet_href)
            add_magnet_transmission_remote(magnet_href)
        return True
    else:
        return False

def url_check_post_id(id):
    if (id > lastUpdateId):
        print("\tWe want to keep downaloading, go to next step")
        return True
    else:
        print("\tWe are not going to scrap this web page any more.")
        return False

def setup_scrap_history(site, cate):
    global lastUpdateId
    tmpIdx = site + "_" + cate
    lastUpdateId = JD.get('history').get(tmpIdx)
    print("lastUpdateId for %s = %d" % (tmpIdx, lastUpdateId))
    return

def endup_scrap_history(site, cate):
    tmp = JD.get('history')

    if (site == 'torrentgirl'):
        if (cate == 'kortv_ent'):
            tmp.update(torrentgirl_kortv_ent = newLatestId)
        elif ( cate == 'kortv_social'):
            tmp.update(torrentgirl_kortv_social = newLatestId)
        else:
            print(tmp)
    elif ( site == 'torrentboza'):
        if (cate == 'kortv_ent'):
            tmp.update(torrentboza_kortv_ent = newLatestId)
        elif ( cate == 'kortv_social'):
            tmp.update(torrentboza_kortv_social = newLatestId)
        else:
            print(tmp)

    JD.set('history', tmp)
    #JD.get('torrent_site').get(site).set('history', tmp)
    return

#url을 기반으로 wr_id text를 뒤의 id parsing 
def get_wr_id(url):
    tmp = url.rfind('-') #torrentgirl의 경우

    if (tmp < 0):
        tmp = url.rfind('wr_id=') #toorentboza일 경우
        if (tmp < 0): # 둘다 검색 못하면 포기
            return 0
        else:
            checkStr = 'wr_id='
    else:
        checkStr = '-'

    startp = tmp+len(checkStr)
    endp = startp
   
    for endp in range(startp,len(url)):
        if (url[endp]).isdigit():
            continue
        else:
            endp = endp-1
            break

    endp = endp+1
    #print((url[startp:endp]))
    return int((url[startp:endp]))

def checkTitleWithTitle(titleKey, title):
    key = JD.get('title_list').get(titleKey).get('title')
    keyArray = key[0].split()
    for tmp in keyArray:
        if not tmp in title:
            return False
    return True

def checkResolutionWithTitle(titleKey, title):
    if JD.get('title_list').get(titleKey).get('resolution') == None:
        return True

    for tmp in JD.get('title_list').get(titleKey).get('resolution'):
        if tmp in title:
            return True
    return False

def checkVersionWithTitle(titleKey, title):
    if JD.get('title_list').get(titleKey).get('version') == None:
        return True

    for tmp in JD.get('title_list').get(titleKey).get('version'):
        if tmp in title:
            return True
    return False

def parse_url(site, cate, url):
    global newLatestId
    global setupNewLatestId
    print('page site : %s, cate : %s, url : %s' % (site, cate, url))
    
    download_format = JD.get('torrent_site').get(site).get('downloadformat').get(cate)
    if not download_format:
        print('download_format : %s, something worng.'  % (download_format))
        exit()

    bsObj = getBsObj(url)
    #실제 게시물 목록만 추출
    compile_format = JD.get('torrent_site').get(site).get('compileformat').get(cate)
    nameList = bsObj.findAll("a", href=re.compile(compile_format))
    #print(nameList)

    for name in nameList:
        url_href = name.attrs['href']
        #print(url_href)

        if not (setupNewLatestId):
            newLatestId = get_wr_id(url_href)
            print("newLatestId :", newLatestId)
            setupNewLatestId = True
        backup_url_href = url_href
        title = name.get_text()    #프로그램의 제목을 가져오는 부분
        #print("title : %s" % title[1:]) #title 첫 글자에 줄바꿈이 포함되어 있음
        
        if (url_href is not None and download_format in url_href):
            for title_idx in JD.get('title_list').keys():
                #debug print("check title : %s, title : %s", (title_idx, title))
                if not checkTitleWithTitle(title_idx, title):
                    continue
                if not checkResolutionWithTitle(title_idx, title):
                    continue
                if not checkVersionWithTitle(title_idx, title):
                    continue

                title = title.replace("\t"," ").replace("\n", " ")
                print("download check with title : " , title)
                if(url_download_torrent(url_href)):
                    break;
                else:
                    return False;

    #print("check post id with title :\n\t" , title[1:])
    if not (url_check_post_id(get_wr_id(backup_url_href))):
        return False;
    return True;

if __name__ == '__main__':

    #####################################################################
    # set you file path
    # For example: 
    # JD = JsonParser("/home/pi/localbin/torrent_crawler_settings.json")
    #####################################################################
    JD = JsonParser("/home/YOUR DIRECTORY/torrent_crawler_settings.json")
    
    for siteIdx in JD.get('torrent_site').keys():
        print("====================================\n=> Try to access site : ", siteIdx)
        urlAddr = JD.get('torrent_site').get(siteIdx).get('url')
        try:
            getBsObj(urlAddr)
        except Exception as e:
            print("Exception access url : %s" % e)
            print("We can not scrwle %s, something wrong.\n" % urlAddr)
            continue

        #print("We are goint parse site : ", JD.get('torrent_site').get(siteIdx))
        for cateIdx in (JD.get('torrent_site').get(siteIdx).get('category')):
            print("site/cate : ", siteIdx, cateIdx)
            setupNewLatestId = False
            setup_scrap_history(siteIdx, cateIdx)
            for count in range(1, 11):                      #10개 페이지까지 탐색 가능
                urlArg = JD.get('torrent_site').get(siteIdx).get('webpageNum').get(cateIdx)+str(count)
                if not (parse_url(siteIdx, cateIdx, urlArg)):
                    break;
            endup_scrap_history(siteIdx, cateIdx)
 
        print("\n")
    exit()

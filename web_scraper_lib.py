#!/usr/bin/env python3
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import subprocess
import csv
import sys
import re
import json
import os.path
import web_scraper_program_list

categoryList = [ "kortv_ent", "kortv_social", "kortv_dra", "movie" ]

def getBsObj(addr):
    req = Request(addr, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read().decode('utf-8','replace')
    data = BeautifulSoup(html, "html.parser")
    return data

def checkUrl(addr):
    try:
        getBsObj(addr)
    except Exception as e:
        print("Exception access url : %s" % e)
        print("We can not scrap %s, something wrong.\n" % addr)
        return False

    return True

def getCateList():
    return categoryList

def getCateIdxFromStr(string):
    return categoryList.index(string)

# targetString: 게시판 제목
def checkTitleWithTitle(title, targetString):
    keyArray = title.lower().split()
    for tmp in keyArray:
        if not tmp in targetString:
            return False
    return True

def checkResolutionWithTitle(resolution, targetString):
    if resolution[0] == None:
        return True

    for tmp in resolution:
        if tmp in targetString:
            return True
    return False

def checkVersionWithTitle(release, targetString):
    if release[0]  == None:
        return True

    for tmp in release:
        tmp = tmp.lower()
        if tmp in targetString:
            return True
    return False

def checkTitleWithProgramList(targetString):
    targetString = targetString.lower()
    for prog in web_scraper_program_list.title_list:
        title = prog[0]
        resolution = prog[1]
        release = prog[2]
        #print(title, resolution, release, targetString)

        if not checkTitleWithTitle(title, targetString):
            #print("checkTitleWithTitle")
            continue
        if not checkResolutionWithTitle(resolution, targetString):
            #print("checkResolutionWithTitle")
            continue
        if not checkVersionWithTitle(release, targetString):
            #print("checkVersionWithTitle")
            continue
        return title
    return False

# targetString: 게시판 제목
def checkTitleWithMovieList(targetString, movie_list_file, video_codec, resolution, year):
    targetString = targetString.lower()
    f = open(movie_list_file, "r", encoding="utf-8")
    lines = f.readlines()

    #print("info, checkTitleWithMovieList targetString = %s, video_codec= %s, resolution = %s, year = %s" % (targetString, video_codec, resolution, year) )
    #sys.exit()

    for line in lines:
        title = line.replace("\n", "")
        title_array = title.split(":")
        #print(titles)

        if not checkTitleWithTitle(title_array[0], targetString):
            #print("checkTitleWithTitle")
            continue
        if len(title_array)>1 and not checkTitleWithTitle(title_array[1], targetString):
            #print("checkTitleWithTitle2")
            continue

        # json에서 불러와서 배열이 아니라서 checkTitleWithTitle 사용
        if not checkTitleWithTitle(resolution, targetString):
            #print("checkResolutionWithTitle")
            continue
        # 위의 이유가 같음.
        if not checkTitleWithTitle(video_codec, targetString):
            #print("checkVersionWithTitle")
            continue
        if not year in targetString:
            continue

        #print("info, checkTitleWithMovieList title = ", title)
        #sys.exit()
        f.close()
        return title

    f.close()
    return False

def check_magnet_history(csv_file, magnet):
    if not os.path.isfile(csv_file):
        return False

    with open(csv_file, 'r', encoding="utf-8") as f:
        ff = csv.reader(f)
        for row in ff:
            if magnet == row[3]:
                print("\t\t-> magnet was already downloaded at web_scraper_history.csv")
                return True
    return False

def add_magnet_info_to_file(csv_file, runtime, sitename, title, magnet, keyword):

    new = [runtime, sitename, title, magnet, keyword]
    with open(csv_file, 'a', newline = '\n', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(new)
    f.close()
    return

#X-Transmission-Session-Id
def get_session_id_torrent_rpc(JD):

    url = "http://%s:%s@%s:%s/transmission/rpc" % (JD.get('trans-id'), JD.get('trans-pw'), JD.get('trans-host'), JD.get('trans-port'))
    res = requests.get(url)
    #print("info, get_session_id_torrent_rpc response = ", res)

    bs = BeautifulSoup(res.text, "html.parser")
    #print("info, get_session_id_torrent_rpc bs = %s" % bs)
    code_text = bs.find('code').text
    #print("info, get_session_id_torrent_rpc code_text =" , code_text)
    #X-Transmission-Session-Id: YeUFW7rotzuLHrx4TfmWCRUF6qVlPd9DcPCEUHzlBcFMXZUd
    array = code_text.split()
    if len(array) == 2 and array[0] == "X-Transmission-Session-Id:":
      session_id ={ array[0].replace(":", "") : array[1]}
      return session_id
    return

def add_magnet_transmission_remote(magnet_addr, JD, download_dir, session_id):

    payload = {
		"arguments":{
			"filename": magnet_addr
		},
		"method": "torrent-add"
    }

    if len(download_dir)>0:
        payload["arguments"]["download-dir"] = download_dir

    res = rpc(JD, payload, session_id)

    return

def get_id_transmission_remote(JD, session_id, torrent_title):
    payload = {
		"arguments":{
			"fields": ["id", "name"]
		},
		"method": "torrent-get"
    }

    res = rpc(JD, payload, session_id)

    for torrent in res.json()["arguments"]["torrents"]:
        if torrent["name"] == torrent_title:
            return torrent["id"]

    return

def get_files_torrent_remote(JD, session_id, torrent_id):

    payload = {
		"arguments":{
			"fields": ["id", "name", "files"]
		},
		"method": "torrent-get"
    }

    res = rpc(JD, payload, session_id)

    for torrent in res.json()["arguments"]["torrents"]:
        if torrent["id"] == torrent_id:
            return torrent["files"]

    return

def rename_file_torrent_prc(JD, torrent_id, session_id, src_file, dest_file):

    json_input = {
        "method": "torrent-rename-path"
    }
    json_input["arguments"] ={"ids": [int(torrent_id)], "path": src_file, "name": dest_file}

    res = rpc(JD, json_input, session_id)

    return

# 상태가 Finished 이고  contain_name 인 토렌트 id를 구해서 삭제
def remove_transmission_remote(JD, session_id, contain_name):

    payload = {
        "arguments":{
            "fields": ["id", "name", "isFinished"]
            },
        "method": "torrent-get"
    }

    res = rpc(JD, payload, session_id)

    for torrent in res["arguments"]["torrents"]:
        if contain_name in torrent["name"] and torrent["isFinished"]:
            payload = {
                "method": "torrent-remove",
                "arguments":{"ids":[torrent["id"]]}
                }
            res = rpc(JD, payload, session_id)

    return

def rpc(JD, payload, session_id):
    url = "http://%s:%s@%s:%s/transmission/rpc" % (JD.get('trans-id'), JD.get('trans-pw'), JD.get('trans-host'), JD.get('trans-port'))
    headers = {'content-type': 'application/json'}
    headers.update(session_id)
    #print("info, rpc header = ", headers)

    print("info, rpc payload = \n", json.dumps(payload, indent=4))
    response = requests.post(
        url, data=json.dumps(payload), headers=headers).json()

    #print("info, rpc resonse =", response.text)

    print("info, rpc response = \n", json.dumps(response, indent=4))
    assert response["result"] == "success"
    #assert response["jsonrpc"]
    #assert response["id"] == 0

    return response

class JsonParser:
    def __init__(self, setfileName):
        self.JsonFile = setfileName
        try:
            dataFile = open(self.JsonFile, 'r')
        except FileNotFoundError as e:
            print(str(e))
            print("Please, set your file path.")
            sys.exit()
        else:
            self.data = json.load(dataFile)
            dataFile.close()

    def get(self, key):
        return (self.data[key])

    def set(self, key, value):
        with open(self.JsonFile, 'w', encoding='utf-8') as dataFile:
            self.data[key] = value
            json.dump(self.data, dataFile, sort_keys = True, ensure_ascii=False, indent = 4)

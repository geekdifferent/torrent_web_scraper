#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import csv
import sys
import re
import json
import os.path
import web_scraper_program_list

categoryList = [ "kortv_ent", "kortv_social" ]

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

def checkTitleWithTitle(title, targetString):
    keyArray = title.split()
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
        title = prog[0].lower()
        resolution = prog[1]
        release = prog[2]
        #print(title, resolution, release)

        if not checkTitleWithTitle(title, targetString):
            continue
        if not checkResolutionWithTitle(resolution, targetString):
            continue
        if not checkVersionWithTitle(release, targetString):
            continue
        return True
    return False

def add_magnet_transmission_remote(magnet_addr, JD):
    cmdArgs = 'transmission-remote %s -n %s:%s -a "%s"' % (JD.get('trans-port'), JD.get('trans-id'), JD.get('trans-pw'), magnet_addr)
    popen = subprocess.Popen(cmdArgs, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return

def check_magnet_history(csv_file, magnet):
    if not os.path.isfile(csv_file):
        return False

    with open(csv_file, 'r') as f:
        ff = csv.reader(f)
        for row in ff:
            if magnet == row[3]:
                print("\t\t-> magnet was already downloaded at web_scraper_history.csv")
                return True
    return False

def add_magnet_info_to_file(csv_file, runtime, sitename, title, magnet):

    new = [runtime, sitename, title, magnet]
    with open(csv_file, 'a', newline = '\n') as f:
        writer = csv.writer(f)
        writer.writerow(new)
    f.close()
    return

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

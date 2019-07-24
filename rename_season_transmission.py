#!/usr/bin/env python3

from datetime import datetime as dtime
import os
import sys
import web_scraper_lib
import web_scraper_program_list
import re

__version__ = 'v1.00'

def set_season_torrent_file(JD, torrent_title, season):

    torrent_id = web_scraper_lib.get_id_transmission_remote(JD, torrent_title)
    print("info, set_season_torrent_file id = %s" % torrent_id)

    session_id = web_scraper_lib.get_session_id_torrent_rpc(JD)
    print("info, set_season_torrent_file session_id = %s" % session_id)

    mp4_file = web_scraper_lib.get_mp4_file_torrent_rpc(JD, torrent_id, session_id)
    print("info set_season_torrent_file mp4_file = %s" % mp4_file)

    dir = os.path.dirname(mp4_file)
    file = os.path.basename(mp4_file)
    replace_string = 's%s\g<epi>' % (season)
    dest_file = re.sub('(?P<epi>E\d+.)', replace_string, file)
    print("info set_season_torrent_file dest_file = %s" % dest_file)

    web_scraper_lib.rename_file_torrent_prc(JD, torrent_id, session_id, mp4_file, dest_file)

    return

if __name__ == '__main__':

    SETTING_PATH = os.path.realpath(os.path.dirname(__file__))+"/"
    SETTING_FILE = SETTING_PATH+"web_scraper_settings.json"
    HISTORY_FILE = SETTING_PATH+"web_scraper_history.csv"
    runTime = dtime.now().strftime("%Y-%m-%d %H:%M:%S")

    print( "%s %s is going to work at %s. %s" % (os.path.basename(__file__),
        __version__, runTime, sys.getdefaultencoding()) )

    JD = web_scraper_lib.JsonParser(SETTING_FILE)

    torrent_title = sys.argv[1]
    print("info, main torrent_title = %s" % torrent_title)

    # 시즌이 설정된 토렌트인가
    for prog in web_scraper_program_list.title_list:

      prog_name = prog[0]
      #print("info, main program name = %s" % prog_name)

      if prog_name in torrent_title and len(prog) == 4:

        set_season_torrent_file(JD, torrent_title, prog[3])

    sys.exit()


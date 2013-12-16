# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import datetime
import threading

import sickbeard

from sickbeard import search_queue
from sickbeard import db, logger


class FailedSearcher():

    def __init__(self):
        self.lock = threading.Lock()

        self.amActive = False

    def _get_season_segments(self, tvdb_id, fromDate):
        myDB = db.DBConnection()
        sqlResults = myDB.select("SELECT DISTINCT(season) as season FROM tv_episodes WHERE showid = ? AND season > 0 and airdate > ?", [tvdb_id, fromDate.toordinal()])
        return [int(x["season"]) for x in sqlResults]

    def _get_air_by_date_segments(self, tvdb_id, fromDate):
        # query the DB for all dates for this show
        myDB = db.DBConnection()
        num_air_by_date_results = myDB.select("SELECT airdate, showid FROM tv_episodes ep, tv_shows show WHERE season != 0 AND ep.showid = show.tvdb_id AND show.paused = 0 ANd ep.airdate > ? AND ep.showid = ?",
                                 [fromDate.toordinal(), tvdb_id])

        # break them apart into month/year strings
        air_by_date_segments = []
        for cur_result in num_air_by_date_results:
            cur_date = datetime.date.fromordinal(int(cur_result["airdate"]))
            cur_date_str = str(cur_date)[:7]
            cur_tvdb_id = int(cur_result["showid"])
            
            cur_result_tuple = (cur_tvdb_id, cur_date_str)
            if cur_result_tuple not in air_by_date_segments:
                air_by_date_segments.append(cur_result_tuple)
        
        return air_by_date_segments

    def run(self):
        
        show_list = sickbeard.showList
        fromDate = datetime.date.fromordinal(1)

        logger.log(u"Beginning search for Failed episodes")
        
        for curShow in show_list:
            
            if curShow.paused:
                continue

            if curShow.air_by_date:
                segments = [x[1] for x in self._get_air_by_date_segments(curShow.tvdbid, fromDate)]
            else:
                segments = self._get_season_segments(curShow.tvdbid, fromDate)

            for cur_segment in segments:
                search_queue_item = search_queue.FailedQueueItem(curShow, cur_segment)
                sickbeard.searchQueueScheduler.action.add_item(search_queue_item) #@UndefinedVariable

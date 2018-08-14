"""Write streaming data to txt-files if needed."""
import logging
import queue

import hwctool.settings
from hwctool.tasks.tasksthread import TasksThread

# from PyQt5.QtCore import pyqtSignal


# create logger
module_logger = logging.getLogger('hwctool.tasks.textfiles')


class TextFilesThread(TasksThread):
    """Write streaming data to txt-files if needed."""

    def __init__(self, matchData):
        """Init the thread."""
        super().__init__()
        self._matchData = matchData
        self._q = SetQueue()
        self._available_items = ['team', 'score', 'meta', 'league']
        self._matchData.dataChanged.connect(self.put)
        self._matchData.metaChangedSignal.connect(self.put)
        self.addTask('write', self.__writeTask)
        self.activateTask('write')

    def put(self, item='meta', *args):
        if item in self._available_items:
            self._q.put(item)

    def __writeTask(self):
        try:
            item = self._q.get(timeout=0.5)
            if item == "team":
                self.__writeTeam()
            elif item == "score":
                self.__writeScore()
            else:
                self.__writeTeam()
                self.__writeScore()
                self.__writeLeague()
        except queue.Empty:
            pass
        finally:
            pass

    def __writeTeam(self):
        file = hwctool.settings.getAbsPath(
            hwctool.settings.casting_data_dir +
            "/teams_vs_long.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(self._matchData.getTeamOrPlayer(0) + ' vs ' +
                    self._matchData.getTeamOrPlayer(1) + "\n")

        file = hwctool.settings.getAbsPath(
            hwctool.settings.casting_data_dir +
            "/teams_vs_short.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(self._matchData.getTeamTag(0) + ' vs ' +
                    self._matchData.getTeamTag(1) + "\n")

        for idx in range(2):
            team = self._matchData.getTeamOrPlayer(idx)
            file = hwctool.settings.getAbsPath(
                hwctool.settings.casting_data_dir +
                "/team{}.txt".format(idx + 1))
            with open(file, mode='w', encoding='utf-8') as f:
                f.write(team)

    def __writeScore(self):
        file = hwctool.settings.getAbsPath(
            hwctool.settings.casting_data_dir + "/score.txt")
        try:
            score = self._matchData.getScore()
            score_str = str(score[0]) + " - " + str(score[1])
        except Exception:
            score_str = "0 - 0"
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(score_str)

    def __writeLeague(self):
        file = hwctool.settings.getAbsPath(
            hwctool.settings.casting_data_dir + "/league.txt")
        with open(file, mode='w', encoding='utf-8') as f:
            f.write(self._matchData.getLeague())


class SetQueue(queue.Queue):
    def _init(self, maxsize):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

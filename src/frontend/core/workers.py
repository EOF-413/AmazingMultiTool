from PyQt5.QtCore import QThread, pyqtSignal

from ...configs.github import fetch_available_repos, RemoteReposError
from .github_importer import import_from_github, GithubImportError


class FetchReposWorker(QThread):
    finished_ok = pyqtSignal(dict)
    finished_error = pyqtSignal(str)

    def run(self):
        try:
            repos = fetch_available_repos()
        except RemoteReposError as e:
            self.finished_error.emit(str(e))
            return
        self.finished_ok.emit(repos)


class InstallWorker(QThread):
    finished_ok = pyqtSignal(str, str)
    finished_error = pyqtSignal(str, str)
    progress = pyqtSignal(str, int)

    def __init__(self, name, github_link, allow_update=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.github_link = github_link
        self.allow_update = allow_update

    def run(self):
        mode = 'update' if self.allow_update else 'install'
        try:
            import_from_github(
                self.github_link,
                allow_update=self.allow_update,
                progress_callback=lambda percent: self.progress.emit(self.name, percent)
            )
        except GithubImportError as e:
            self.finished_error.emit(self.name, str(e))
            return
        self.finished_ok.emit(self.name, mode)

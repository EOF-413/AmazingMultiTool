import os
from os import path

from PyQt5.QtCore import QObject, QProcess, pyqtSignal

from ...backend.debug import Log
from ...backend.constants import MARKER, get_python_executable, ensure_amt_api_written


class ProcessManager(QObject):
    message = pyqtSignal(str, str, object)
    stopped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._processes = {}

    def is_running(self, name):
        return name in self._processes

    def start(self, name, main_path):
        if self.is_running(name):
            return

        python_exe = get_python_executable()
        if python_exe is None:
            self.message.emit(
                name,
                'Не найден интерпретатор Python. Укажите путь к python.exe в настройках приложения.',
                'red'
            )
            return

        process = QProcess(self)
        process.setProgram(python_exe)
        process.setArguments(['-u', main_path])
        process.setWorkingDirectory(path.dirname(main_path))

        shared_dir = ensure_amt_api_written()
        env = process.processEnvironment()
        env.insert('PYTHONIOENCODING', 'utf-8')

        parent_appdata = os.environ.get('APPDATA')
        if parent_appdata:
            env.insert('APPDATA', parent_appdata)
        else:
            userprofile = os.environ.get('USERPROFILE')
            if userprofile:
                env.insert('APPDATA', os.path.join(userprofile, 'AppData', 'Roaming'))

        existing = env.value('PYTHONPATH')
        env.insert('PYTHONPATH', shared_dir + (path.pathsep + existing if existing else ''))
        process.setProcessEnvironment(env)

        process.readyReadStandardOutput.connect(lambda: self._read_stdout(name, process))
        process.readyReadStandardError.connect(lambda: self._read_stderr(name, process))
        process.finished.connect(lambda *_: self._on_finished(name))

        self._processes[name] = process
        process.start()
        Log.info(f"Запущена модификация [{name}] интерпретатором [{python_exe}].")

    def stop(self, name):
        process = self._processes.get(name)
        if process is None:
            return
        process.kill()

    def _read_stdout(self, name, process):
        data = bytes(process.readAllStandardOutput())
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('cp1251', errors='replace')

        for line in text.splitlines():
            if not line:
                continue
            color = None
            text_line = line
            if line.startswith(MARKER):
                try:
                    _, rest = line.split(MARKER, 1)
                    color, text_line = rest.split('%%', 1)
                except ValueError:
                    text_line = line
            self.message.emit(name, text_line, color)

    def _read_stderr(self, name, process):
        data = bytes(process.readAllStandardError())
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('cp1251', errors='replace')

        for line in text.splitlines():
            if line:
                self.message.emit(name, line, 'red')

    def _on_finished(self, name):
        self._processes.pop(name, None)
        Log.info(f"Модификация [{name}] завершена.")
        self.stopped.emit(name)

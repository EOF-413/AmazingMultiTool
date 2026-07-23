import os
import sys
import shutil
import subprocess


def clean_dist():
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    build_dir = os.path.join(os.path.dirname(__file__), 'build')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)


def build():
    print("Начинаю сборку AMT...")

    try:
        subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        print("PyInstaller не установлен. Устанавливаю...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
            check=True
        )

    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        '--onedir',
        '--noconsole',
        '--name', 'AMT',
        '--icon', 'icon.ico',
        '--add-data', 'icon.ico;.',
        '--add-data', 'src;src',
        '--hidden-import', 'PyQt5.sip',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'PyQt5.QtGui',
        'main.py'
    ]

    print(f"Выполняю: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"Ошибка сборки! Код: {result.returncode}")
        sys.exit(result.returncode)

    print("\nСборка завершена успешно!")
    print(f"Результат: {os.path.abspath('dist/AMT/AMT.exe')}")


def main():
    clean_dist()
    build()


if __name__ == '__main__':
    main()

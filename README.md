# 🧰 Amazing MultiTool (AMT)

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11.0-purple.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.1.0-red.svg)](https://github.com/EOF-413/AmazingMultiTool)
[![Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://github.com/EOF-413/AmazingMultiTool)
[![Linux](https://img.shields.io/badge/platform-Linux-orange.svg)](https://github.com/EOF-413/AmazingMultiTool)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

**AMT** — это универсальный лаунчер и менеджер модификаций, написанный на Python 3.11 с использованием PyQt5. Он позволяет легко устанавливать, запускать и управлять плагинами (модификациями) для автоматизации игровых процессов.

---

## 🚀 Быстрый старт

### 1. Скачайте ядро системы

Перейдите на страницу релизов: [https://github.com/EOF-413/AmazingMultiTool/releases](https://github.com/EOF-413/AmazingMultiTool/releases)

Запустите установщик `AMT_Setup_X.Y.Z_base.exe`.

### 2. Добавьте модификацию

- На главном экране нажмите на плитку **«Добавить модификацию»**.
- Выберите **«Импортировать из GitHub»**.
- Вставьте ссылку на репозиторий модификации.

Модификация автоматически скачается и появится в интерфейсе.

### 3. Запустите модификацию

- Нажмите зелёную кнопку **▶** на тайле модификации — откроется консоль.
- Внутри консоли используйте горячую клавишу (обычно **F9**) для старта/остановки бота.

---

## 📦 Сборка из исходников

Если вы хотите собрать AMT самостоятельно:

```bash
# Установите зависимости
pip install -r requirements.txt
pip install pyinstaller

# Соберите --onedir exe
pyinstaller --onedir --noconsole --name AMT main.py
```

## 🧩 Структура модификации

Каждая модификация — это папка в plugins/bots/ со следующей структурой:
```text
plugins/bots/Название/
├── manifest.json       # описание модификации
├── main.py             # точка входа
├── icon.ico            # иконка
├── requirements.txt    # зависимости (устанавливаются автоматически)
└── ... (любые другие файлы)
```

## Пример manifest.json:
```json
{
    "APP": ["bots", "MyMod"],
    "APP_NAME": ["My", "Awesome", "Mod"],
    "APP_VERSION": {
        "VER": "1.0.0",
        "DAT": "01.01.2026",
        "DEV": "YourName"
    },
    "APP_GITHUB_LINK": {
        "GIT": "https://github.com",
        "DEV": "YourName",
        "REP": "MyMod"
    }
}
```

## 🛠 Требования

```text
Python 3.11 (для запуска модификаций)
Установленные зависимости модификации (устанавливаются автоматически при первом запуске)
```

## 🤝 Вклад

```text
Мы приветствуем ваши идеи и улучшения!
Создавайте Issue и Pull Request в репозитории проекта.
```

## 📄 Лицензия

```text
Проект распространяется под лицензией MIT.
```

[![Терминал статистики GitHub](https://github-stats-terminal-style-five.vercel.app/api/stats?username=EOF-413%2FAmazingMultiTool&theme=hacker&headerStyle=mac&typingSpeed=100&hostname=github.com&commands=languages%2Cneofetch%2Cgit-log%2Cexit&sourceType=repo&target=EOF-413%2FAmazingMultiTool)](https://github.com/EOF-413/AmazingMultiTool)

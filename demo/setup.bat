@echo off
chcp 65001 >nul
echo ======================================
echo  Установка системы мониторинга книг
echo ======================================
echo.

:: Переход в папку проекта
cd /d "D:\A FREELANCE\parser"

:: 1. Проверка Python
echo [1/6] Проверка Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python не найден!
    echo Пожалуйста, установите Python с python.org
    echo Не забудьте поставить галочку Add Python to PATH
    pause
    exit /b
)
echo Python найден.

:: 2. Установка библиотек
echo [2/6] Установка библиотек...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet streamlit pandas psycopg2-binary requests
echo Библиотеки установлены.

:: 3. Проверка/создание базы данных
echo [3/6] Настройка базы данных...

:: Создаём SQL-файл для инициализации (временный)
echo CREATE DATABASE books_monitor; > init_db.sql
echo \c books_monitor; >> init_db.sql
echo CREATE TABLE IF NOT EXISTS books ( >> init_db.sql
echo     id SERIAL PRIMARY KEY, >> init_db.sql
echo     title TEXT NOT NULL, >> init_db.sql
echo     rank INTEGER, >> init_db.sql
echo     collected_date DATE DEFAULT CURRENT_DATE >> init_db.sql
echo ); >> init_db.sql
echo CREATE TABLE IF NOT EXISTS books_history ( >> init_db.sql
echo     id SERIAL PRIMARY KEY, >> init_db.sql
echo     book_id INTEGER REFERENCES books(id), >> init_db.sql
echo     title TEXT, >> init_db.sql
echo     rank INTEGER, >> init_db.sql
echo     change_date DATE DEFAULT CURRENT_DATE >> init_db.sql
echo ); >> init_db.sql

:: Выполняем SQL
psql -U postgres -f init_db.sql >nul 2>nul
del init_db.sql
echo База данных настроена.

:: 4. Создание задания в планировщике Windows
echo [4/6] Настройка автоматического запуска...
schtasks /create /tn "DailyBookParser" /tr "python \"%cd%\parser.py\"" /sc daily /st 09:00 /f >nul 2>nul
echo Задание добавлено в планировщик (каждый день в 9:00).

:: 5. Создание ярлыка для дашборда
echo [5/6] Создание ярлыка для запуска дашборда...
echo @echo off > start_dashboard.bat
echo cd /d "%cd%" >> start_dashboard.bat
echo streamlit run dashboard.py --server.headless false >> start_dashboard.bat
echo pause >> start_dashboard.bat
echo Ярлык start_dashboard.bat создан.

:: 6. Первый запуск парсера (проверка)
echo [6/6] Первый запуск парсера (проверка)...
python parser.py

echo.
echo ======================================
echo  Установка завершена!
echo ======================================
echo.
echo Для запуска дашборда дважды кликни на start_dashboard.bat
echo Парсер будет запускаться каждый день в 9:00 автоматически
echo.
pause
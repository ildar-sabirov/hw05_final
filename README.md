## О проекте:

Yatube - платформа для обмена публикациями. Здесь вы можете вести свой блог, публиковать посты, подписываться на интересные группы и авторов, а также оставлять комментарии к постам.

## Технологии:

- Python 3.9
- Django==2.2.28
- mixer==7.1.2
- Pillow==9.0.1
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- requests==2.26.0
- six==1.16.0
- sorl-thumbnail==12.7.0
- Pillow==9.0.1
- django-environ==0.8.1

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ildar-sabirov/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

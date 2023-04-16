# YaTube

## Описание
Данный проект представляет собой социальную сеть для блогеров.

### Реализован функционал дающий возможность:
* Подписываться на пользователя.
* Просматривать, создавать новые, удалять и изменять посты.
* Просматривать и создавать группы.
* Комментировать, смотреть, удалять и обновлять комментарии.
* Оценивать посты.

### Используемые в проекте технологии:
![python](https://img.shields.io/badge/Python-100000?style=for-the-badge&logo=python&logoColor=white) ![django](https://img.shields.io/badge/django-100000?style=for-the-badge&logo=django&logoColor=white) ![github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white) ![vscode](https://img.shields.io/badge/VSCode-100000?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)

### Автор - Вячеслав Клепалов.
Мои социальные сети:
[![telegram](https://img.shields.io/badge/Telegram-100000?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/prived_medved) [![whatsapp](https://img.shields.io/badge/WhatsApp-100000?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/79123071758) [![github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/KlepalovS)

## Установка 
Клонируем репозиторий на локальную машину:

```$ git clone https://github.com/KlepalovS/api_final_yatube.git```

 Создаем виртуальное окружение:
 
 ```$ python -m venv venv```
 
 Устанавливаем зависимости:

```$ pip install -r requirements.txt```

Создание и применение миграций:

```$ python manage.py makemigrations``` и ```$ python manage.py migrate```

Запускаем сервер:

```$ python manage.py runserver```
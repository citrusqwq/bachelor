# ViViPlayer-1

## Installation
Im Stammverzeichnis den folgenden Befehl ausführen zum Starten des Projekts.
```
    docker-compose up -d --build
```

> TODO

- Zertifikat setzen
- SMTP Server Variablen setzen
- andere ENV Variablen setzen

Meim ersten Start muss der Superuser wie folgt erstellt werden.
```
    docker exec -it <Name des Stammverzeichnis>_djangoapp_1 bash
    # falls der Container nicht gefunden werden kann -> 'docker ps' und richtigen name finden
    python manage.py createsuperuser
```

Zum Beenden ebenfalls im Stammverzeichnis.
```
    docker-compose stop
```

## Entwicklung

### 1. Ein pip-Environment erstellen bzw das Bestehende updaten:
```
    pipenv install
```
<br>

### 2. Das pip-Environment starten:
```
    pipenv shell
```
<br>

### 3. Wenn Änderungen am Projekt mit der Datenbak (db.sqlite3) synchorinsiert weden müssen:
Achtung: Wenn eine bestehende Datenbank noch andere Models enthält, sollte sie gelöscht werden (ggf. Backup machen). In dem Fall wird im Anschluss eine neue Datenbank erstellt. <br>
Achtung: Da die bestehenden Superuser Accounts in der Datenbank gespeichert sind, werden diese beim löschen der Datenbank auch gelöscht.
```
    python manage.py migrate
```
<br>

### 4. Wenn es noch keinen Moderator Account (django Superuser) gibt, diesen erstellen:
```
    python manage.py createsuperuser
```
<br>

### 5. Den Server starten:
```
    python manage.py runserver
```
<br>

## Dokumentation
Dokumentation für die Websocket Kommunikation [hier](./doc/websocket/README.md).

Alte Dokumentation für die Websocket Kommunikation [hier](./api/README.md).

# Credits

### [custom-user-model](https://github.com/testdrivenio/django-custom-user-model/)

<details>
  <summary>MIT</summary>

    MIT License

    Copyright (c) 2021 Michael Herman

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.


</details>
